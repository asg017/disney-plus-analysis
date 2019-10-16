import streamlit as st
import pandas as pd

@st.cache
def get_tweets():
    return pd.read_json('all_raw_tweets.json.gz', dtype={
        'in_reply_to_status_id_str':str,
        'id_str':str
        })

@st.cache
def save_titles(titles):
    titles.to_csv('titles.csv.gz')

st.title("Disney-Plus Content Twitter Thread")

"""

Yesterday morning, the Disney+ Twitter account tweeted [a thread](https://twitter.com/disneyplus/status/1183715553057239040) 
listing every single title that is coming to the Disney+ platform later this month.

The thread contained ~600 tweets ranging from [Snow White and the Seven Dwarfs](https://twitter.com/disneyplus/status/1183715564209893377) (1937) to [The Mandalorian]() (2019). They tweeted all these titles, in chronological order, one-by-one. Let's take a deeper look at the thread:

"""

df = get_tweets()

source_tweet_id = '1183715553057239040'

replies = {}

for index, row in df.iterrows():
    reply_parent = row['in_reply_to_status_id_str']
    if reply_parent is not None:
        if replies.get(reply_parent) is None:
            replies[reply_parent] = [row['id_str']]
        else:
            replies[reply_parent].append(row['id_str'])

def get_thread(source, replies):
    a = [source]
    ptr = replies[source]
    while ptr is not None:
        a.append(ptr[0])
        ptr = replies.get(ptr[0])
    return a

thread_tweets = get_thread(source_tweet_id, replies)

thread = df[df.id_str.isin(thread_tweets)]

thread["release_year"] = thread.text.str.extract(r'\(([^)]*)\)[^(]*$')
thread["title"] = thread.text.str.split(' \(', n=1).str.get(0)

titles = thread[~thread["release_year"].isnull()]
titles["release_year_int"] = titles.release_year.astype(int)

save_titles(titles)

"""
I used the Twitter API to fetch all @disneyplus tweets, then did some general 
cleaning/organizing of that entire list. If you wanna know more, check this box:
"""

if st.checkbox("Show me the nerdy data stuff!"):

    """
    First, I scraped all the tweets from the Disney+ Twitter account - including tweets that aren't in the giant thread. That dataset looks like this:
    """

    df


    st.markdown("""
    Then, I filtered in down to just the tweets that are in reply to the orignal tweet (and its children). This was a little complicated. I manually found the ID of the first tweet in the thread `{source_tweet_id}`, then found any other tweet that had an `in_reply_to_status_id` value of that (or a tweet id that did). This now gave us a filtered list of just the tweets that appeared in the thread:

    """.format(source_tweet_id=source_tweet_id))
    
    st.write(thread)
    
    """But to make it even cooler, we can parse through the `text` attribute of each tweet and extract some more structured data. For example, each tweet reads like `Title Name (release year)`. So, using some regex that I totally googled, we can get a `release_year` and `name` attribute for each tweet - and for the tweets that don't follow this format (the first and last tweet, that don't talk about titles), we can simply remove them from the dataset so we are left with a cleaned, filtered list of just the tweets that announced a Disney title (and some metadata about each title).
    """
    
    st.write(titles)
    
    """
    And that's all the data processing! Let's go back to the show
    """

min_tweet_date = thread.created_at.min()
max_tweet_date = thread.created_at.max()
st.markdown("""
We have all `{count}` tweets from the thread - ranging from 
`{first_date}` to `{last_date}`, only taking `` minutes to tweet. 
""".format(count=len(thread), 
        first_date= min_tweet_date,
        last_date= max_tweet_date,
        )
)

"""
Of all the titles listed, here are 



"""

st.markdown("""
<iframe src="https://onb-host.glitch.me/notebook?notebook=@d3/bar-chart&targets=chart,x,y,data" width="100%" height="500px" ></iframe>
""", True)

st.vega_lite_chart(titles, {
  "mark": "bar",
  "encoding": {
    "x": {"field": "release_year", "type": "temporal"},
    "y": {"field": "retweet_count", "type": "quantitative", "aggregate":"count"}
  }
})


st.subheader("Most favorited")
st.table(titles[['title', 'release_year', 'favorite_count']].sort_values('favorite_count', ascending=False).head(10))

st.subheader("Most retweeted")
st.table(titles[['title', 'release_year', 'retweet_count']].sort_values('retweet_count', ascending=False).head(10))

year_range = st.slider("Select a time range to view", 
        int(titles.release_year.min()),
        int(titles.release_year.max()),
        (int(2000), int(2015))
        )

a = titles[titles['release_year_int'].between(*year_range)][["title", "release_year", "favorite_count"]].sort_values('favorite_count', ascending=False)

st.table(a)


# https://www.dizavenue.com/2015/08/the-7-eras-of-disney-filmmaking.html
eras = (
        ("Golden Age", 1937, 1942),
        ("Wartime Era", 1943, 1949),
        ("Silver Age", 1950, 1959),
        ("Bronze Age", 1970, 1988),
        ("Disney Renaissance", 1989, 1999),
        ("Post Renaissance Era", 2000, 2009),
        ("The Revival Era", 2010, 2019)
)

st.subheader("Disney Titles - Hall of Fame by Era")

for era in eras:
    st.table()

era = st.selectbox("Disney Era", eras, format_func=lambda era: "{} ({}-{})".format(*era))

st.subheader("Twitter's favorite Disney Titles during the {name} ({range})".format(name=era[0], range="{}-{}".format(era[1], era[2])))

st.table(titles[titles["release_year_int"].between(era[1], era[2])][["title", "release_year", "favorite_count"]].sort_values("favorite_count", ascending=False) )
