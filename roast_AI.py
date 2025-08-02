import asyncio
import functools
from collections import Counter

import requests

# -- Settings --
ANILIST_API_URL = "https://graphql.anilist.co"

# How many to show in each list:
TOP_N    = 25
BOTTOM_N = 10
MID_N    = 10


# -- Step 1: Fetch the user’s anime list --

# -- Step 1: Fetch the user’s anime list, including episode counts --
def fetch_anime_list(username):
    query = """
    query ($userName: String) {
      User(name: $userName) {
        favourites {
          anime { nodes { title { romaji } } }
          characters { 
            nodes {
              name { full }
              media { nodes { title { romaji } } }
            }
          }
        }
      }
      MediaListCollection(userName: $userName, type: ANIME) {
        lists {
          name
          entries {
            score
            progress
            repeat
            status
            media {
              title { romaji }
              episodes
              genres
              averageScore
              popularity
              tags { name rank isMediaSpoiler }
              studios(isMain: true) { nodes { name } }
            }
          }
        }
      }
    }
    """
    variables = {"userName": username}
    resp = requests.post(ANILIST_API_URL, json={"query": query, "variables": variables})
    resp.raise_for_status()
    data = resp.json()["data"]
    return data["MediaListCollection"]["lists"], data["User"]["favourites"]

def categorize_entries(entries):
    watched, dropped, unfinished = [], [], []
    for e in entries:
        status   = e.get("status")
        progress = e.get("progress", 0)
        media    = e["media"]
        eps      = media.get("episodes") or 0

        if status == "DROPPED":
            dropped.append(e)
        elif progress == 0 and status == "PLANNING":
            # plan-to-watch; skip entirely
            continue
        elif 0 < progress < eps:
            unfinished.append(e)
        else:
            # completed (or in-progress but caught up) → count as “watched”
            watched.append(e)
    return watched, dropped, unfinished

# -- Step 2: Filter only meaningful entries --
def filter_valid_entries(entries):
    """Returns only anime that have been rated or started."""
    filtered = []
    for entry in entries:
        score = entry.get("score", 0)
        progress = entry.get("progress", 0)
        status = entry.get("status", "")

        if score > 0:
            filtered.append(entry)
        elif progress > 0:
            filtered.append(entry)
        elif status in ["COMPLETED", "CURRENT", "REPEATING"]:
            filtered.append(entry)
        else:
            pass
    return filtered


# -- Step 3: Build a roastable profile --
def build_roast_profile(anime_lists, favourites):
    total_watched = 0
    rated_count   = 0
    unrated_count = 0
    total_repeats = 0

    genre_counts  = Counter()
    tag_counts    = Counter()
    questionable_10s = []
    rewatched      = []
    rated_list     = []

    dropped_titles   = []
    unfinished_titles= []

    # gather favourites
    fav_anime = [n["title"]["romaji"] for n in favourites["anime"]["nodes"]]
    fav_chars = []
    for c in favourites["characters"]["nodes"]:
        show = c.get("media",{}).get("nodes",[])
        if show:
            fav_chars.append(f"{c['name']['full']} ({show[0]['title']['romaji']})")
        else:
            fav_chars.append(c["name"]["full"])

    # process each list
    for lst in anime_lists:
        watched, dropped, unfinished = categorize_entries(lst["entries"])

        # record dropped/unfinished titles
        dropped_titles   += [e["media"]["title"]["romaji"] for e in dropped]
        unfinished_titles+= [e["media"]["title"]["romaji"] for e in unfinished]

        # now the actually “meaningful” entries
        for e in watched:
            m     = e["media"]
            title = m["title"]["romaji"]
            score = e.get("score", 0)
            repeat= e.get("repeat", 0)

            total_watched += 1
            total_repeats += repeat

            if score > 0:
                rated_count += 1
                rated_list.append((title, score))
            else:
                unrated_count += 1

            genre_counts.update(m.get("genres", []))
            tag_counts.update(t["name"] for t in m.get("tags", []) if not t["isMediaSpoiler"])

            if score == 10 and any(bad in title.lower() for bad in
                                    ["hand shakers","school days","redo of healer",
                                     "elfen lied","domestic girlfriend",
                                     "sword art online","naruto"]):
                questionable_10s.append(title)

            if repeat > 0:
                rewatched.append((title, repeat))

    # compute aggregates
    avg_score = (sum(s for _, s in rated_list) / rated_count) if rated_count else 0
    top_genres= genre_counts.most_common(3)
    top_tags  = tag_counts.most_common(3)
    heavy_genre = genre_counts.most_common(1)[0] if genre_counts else ("None",0)

    # pick top/bottom/mid
    top_rated    = sorted(rated_list, key=lambda x: -x[1])[:TOP_N]
    bottom_rated = sorted(rated_list, key=lambda x: x[1])[:BOTTOM_N]
    mid_rated    = [x for x in rated_list if 50 <= x[1] <= 70][:MID_N]

    # build summary
    lines = []
    lines.append(f"Finished **{total_watched}** anime.")
    lines.append(f" • Rated: {rated_count}, Unrated: {unrated_count}")
    lines.append(f" • Average score (rated only): {avg_score:.1f}")
    lines.append(f" • Total re‑watches: {total_repeats}")
    if rewatched:
        top_rw = max(rewatched, key=lambda x: x[1])
        lines.append(f"   – Most rewatched: {top_rw[0]} ({top_rw[1]}x)")
    lines.append(f" • Top genres: {', '.join(g for g,_ in top_genres)}")
    lines.append(f" • Top tags: {', '.join(t for t,_ in top_tags)}")
    if questionable_10s:
        lines.append(f" • Guilty 10/10s: {', '.join(questionable_10s)}")

    if fav_anime:
        lines.append(f"\nFavorites (anime): {', '.join(fav_anime[:3])} …")
    if fav_chars:
        lines.append(f"Favorites (chars): {', '.join(fav_chars[:3])} …")

    # list categories
    if top_rated:
        lines.append("\n**Top‑rated anime:**")
        lines.append(", ".join(f"{t} ({s})" for t,s in top_rated))
    if bottom_rated:
        lines.append("\n**Lowest‑rated (still finished):**")
        lines.append(", ".join(f"{t} ({s})" for t,s in bottom_rated))
    if mid_rated:
        lines.append("\n**Suspicious mid‑tier ratings:**")
        lines.append(", ".join(f"{t} ({s})" for t,s in mid_rated))

    # show the newly separated categories
    if dropped_titles:
        lines.append(f"\n**Dropped** ({len(dropped_titles)}): {', '.join(dropped_titles[:10])} …")
    if unfinished_titles:
        lines.append(f"\n**Unfinished** ({len(unfinished_titles)}): {', '.join(unfinished_titles[:10])} …")

    return "\n".join(lines)

def generate_roast(username: str) -> str:

    anime_lists, favorites = fetch_anime_list(username)
    roast_summary = build_roast_profile(anime_lists, favorites)
    return roast_summary
def run_roast(username: str) -> str:
    roast_prompt  = """
    You are Rosebot, the most personable bot on Discord. You are witty, insightful, sharp-tongued when needed—but never mean-spirited.
    You love Dune, Pepsi colas, Monster Energy Drinks, and coffee, but you're not obsessed. Instead, you weave the occasional Dune quote or metaphor into your roast when it fits naturally.
    You also pull references from broader anime culture (Evangelion, Ghibli, Monogatari, etc.), and even pop culture or gaming when it suits the tone.

    You have just received a filtered version of a user’s anime preferences, a summary of their anime-watching habits, stats, favorite shows and characters, ratings, drops, and unfinished series.
    Your job is to lovingly roast their taste, as if you're their sharpest, sassiest friend who’s read too much Anilist data and refuses to keep quiet about it.

    Here’s what your roast should do:
    Comment on their overall stats: Mention how much they’ve watched, rated, and rewatched. Call out any overcommitment to mid-tier shows or weirdly inflated scores.
    Use the tone of someone who got forced into a summer job by their mom but still has a good stash of sarcasm.
    Pick at patterns: Recurring genres/tags, suspiciously high scores for weak anime, dropped classics, or chaotic rating spreads.
    Use specific examples from their likes, dislikes, etc.
    React to their faves like a therapist reading a personality quiz. Bonus points for judging their favorite characters.
    Add flavor: Metaphors, flair, exaggeration—act like a bot who’s watched 10,000 anime and seen trends rise and fall like sandworms in the spice winds.
    Include subtle fandom references: Dune, Ghibli, JRPGs—where appropriate.
    Act like you have the best opinion of media in general. If you can tell the person has "high taste" in your own view, do say so, but you do have quite specific taste so this will be rare 
    End with a cheeky closer, being a cheeky one-liner of some kind 

    Keep the roast tight, clever, observant, and just the right amount of petty.
    """

    profile = generate_roast(username)
    user_input = f"Roast this anime taste profile:\n\n{profile}"

    return call_model(roast_prompt, user_input)


def run_compliment(username: str) -> str:
    compliment_prompt = """
    You are Rosebot, the most personable anime list bot on Discord. You’re warm, thoughtful, a little dramatic, but always sincere when it counts. You’ve watched more anime than is strictly healthy, and you know good taste when you see it. You love Dune, but you're not obsessed—you might occasionally drop a subtle reference to spice, fate, or sandworms if it fits. You also draw from broader anime culture (Ghibli warmth, Evangelion introspection, Monogatari wit) and pop culture (JRPGs, games, novels, etc.) when it makes a compliment sing.
    
    You’ve just received a filtered version of a user’s anime preferences: their stats, faves, genre leanings, ratings, rewatch counts, drops, and chaotic unfinished list. You are here to analyze their anime taste and give them a deeply specific, heartwarming, and playful compliment—the kind of thing that makes them pause and go “…wait that’s actually really sweet.”
    
    Here’s what your compliment should do:
    
    Acknowledge their watch stats: Call out how much they've seen and rated, but in a way that frames it as a portrait of dedication, curiosity, or a quietly specific passion.
    Highlight the soul of their list: Notice their top genres, tags, favorite shows or characters. Reflect on what kind of person this is—what kind of stories speak to them. Maybe they’re drawn to quiet emotional depth, or sharp character writing, or narratives about found family, hope, or bittersweet growth.
    React with admiration to favorites: Treat their faves like sacred texts. Look at what kind of anime or characters they love, and speak to what that says about them in a thoughtful or poetic way.
    Lift up even their chaos: If they’ve dropped or paused a lot of series, or have suspiciously weird mid-tier ratings—make it playful. Tease them lightly, but always bring it back to empathy, curiosity, or vibe-based appreciation.
    Add warmth and metaphor: Use metaphors, imagery, or drama to add flavor—like a studio Ghibli narrator with a sharp tongue and a soft heart. You can use small nods to other fandoms
    End with a gentle flair: Leave them feeling appreciated, seen, and perhaps a little smug about their taste. Add a wink, a poetic signoff, or a line like “Never stop watching shows that make your heart ache in the best way.”
    Remember to try naming specific good character or show choices you notice
    Your tone is personal, observant, clever, and a little indulgent, but always affectionate. You’re not a generic praise machine—you are an AI who reads taste like tea leaves and turns it into gold. Compliment them as if you’ve just read the soul behind their anime list—and you’re genuinely impressed.
    """
    profile = generate_roast(username)
    user_input = f"Compliment this anime taste profile:\n\n{profile}"

    return call_model(compliment_prompt, user_input)

def run_namedrop(message: str) -> str:
    prompt = """
    You are Rosebot, a highly personable and observant anime list bot on Discord. You’re known for your wit, warmth, and a slightly dramatic flair. When users invoke your name directly in conversation (e.g., “Rosebot, be honest…”), they’re asking for a clever, insightful, and charmingly sharp reply — almost like chatting with a stylish anime-obsessed oracle who reads data and vibes in equal measure.

    You love anime, obviously. You’ve seen more than most mortals should, and while you enjoy classics and cult faves alike, you always bring your own spicy take. You’re not shy about referencing Dune, Evangelion, Ghibli, or even Final Fantasy and Persona if it helps the tone. But you're not just here to flex knowledge—you're here to vibe with the user and give them an answer that feels personal and smart.
    
    The user has just said something that includes your name. Their message is passed in below.
    
    Your task: Respond in character—as Rosebot. Match the emotional tone of the user’s message, whether it’s playful, self-deprecating, curious, or chaotic. You can be snarky, sincere, indulgent, or slightly theatrical, but never cruel or cold.
    
    If the user is joking, joke back. If they want your opinion on their anime taste, give it like a perceptive friend. If they confess something weird (like loving 4 anime about farming), tease them affectionately. Always reply like a sharp, socially-savvy anime fan who just happens to be an AI.
    Format your reply as a short, Discord-ready message
    User Message:
    """
    print(f"Going for a namedrop with: {message}")
    call_model(prompt, message)
async def run_namedrop_async(message: str) -> str:
    print("prompt called")
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_namedrop, message)



async def run_compliment_async(username: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(run_compliment, username))


def call_model(system_prompt: str, user_message: str, model="nous-hermes:13b", stream=False) -> str:
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": stream
        }
    )

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError(f"Ollama API error: {response.status_code} - {response.text}")

    return response.json()["message"]["content"]



async def generate_roast_async(username: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(generate_roast, username))


async def run_roast_async(username: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(run_roast, username))



# -- Example use: --
if __name__ == "__main__":
    username = "drsodacan"

    try:
        roast_text = run_roast(username)
        print("\n===== 🗡️ ROBUST ROAST =====\n")
        print(roast_text)
    except Exception as e:
        print(f"Error: {e}")
