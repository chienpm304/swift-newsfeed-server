from utils import * 

# Constants
slugs = ["development", "updates", "packages", "design", "marketing", "companies", "podcasts", "newsletters", "youtube", "twitch"]
unsupported_site_urls = load_txt_lines('unsupported_site_urls.txt')
IS_DEBUG = True

def rebuild_sites():
    data = load_json('./categories.json')

    all_sites = []
    for category in data.get("categories", []):
        category_title = category.get("title", "")
        category_slug = category.get("slug", "")
        
        sites = category.get("sites", [])
        for site in sites:
            site_dict = {
                "title": site.get("title", ""),
                "site_url": site.get("site_url", ""),
                "feed_url": site.get("feed_url", ""),
                "category": category_title,
                "slug": category_slug
            }
            all_sites.append(site_dict)

    sites_json = {
        "updated": current_timestamp(),
        "sites": all_sites
    }
    save_json(sites_json, 'sites.json')

    return all_sites

def parse_feed(site):
    site_url = site['site_url']
    feed_url = site['feed_url']

    if site_url in unsupported_site_urls:
        raise Exception("Unsupported site_url")

    print(f"> Parsing {feed_url}...")
    feed = feedparser.parse(feed_url)
    posts = []
    for entry in feed.entries:
        dt_object = parser.parse(entry.updated, tzinfos=custom_tzinfos)
        updated = int(dt_object.timestamp())

        post_dict = {
            "id": entry.id,
            "title": entry.title,
            "link": entry.link,
            "updated": updated,
            "site_url": site_url
        }
        posts.append(post_dict)

    return posts

def generate_posts_by_sites(sites):
    for site in sites:
        try:
            output_file_path = './posts/by_site/' + simplifized_url(site['site_url']) + '.json'
            print(f"processing {output_file_path}")

            if IS_DEBUG and os.path.isfile(output_file_path):
                print(f"[debug] Skipped: {output_file_path}")
                posts = load_json(output_file_path)["posts"]
            else:
                posts = parse_feed(site)
            
            if not posts:
                raise Exception("empty posts")
            else:
                posts_result = {
                    "updated": current_timestamp(),
                    "posts": posts
                }
                save_json(posts_result, output_file_path)

        except Exception as e:
            print(f"❌ Error parsing, {site['site_url']}, error: {str(e)}")
        
# main 

# 1. Download blogs json file from github repo
blogs = load_json_from_url("https://raw.githubusercontent.com/daveverwer/iOSDevDirectory/main/blogs.json")
save_json(blogs, 'blogs.json')

# 2. Generate `sites.json` - array of Site
sites = rebuild_sites()

# 3. Generate `posts/by_site/{simplifized_site_url}_posts.json`s
generate_posts_by_sites(sites)

# 4. Generate `posts/by_slug/{slug}.json}

# print(all_feeds)

# Sort by updated and save to `feeds.json`
# all_feeds.sort(reverse=True, key=lambda feed: feed['updated'])
# feeds_json = {
#     "updated": current_timestamp(),
#     "feeds": all_feeds
# }
# save_json(feeds_json, 'feeds.json')