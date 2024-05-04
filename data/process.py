from utils import * 

# Constants
SUPPORTED_SLUGS = ["development", "updates", "packages", "design", "marketing", "companies", "podcasts", "newsletters", "youtube", "twitch"]
UNSUPPORTED_SITE_URLS = load_txt_lines("unsupported_site_urls.txt")
IS_DEBUG = True
LIMIT_NUMBER_OF_POST_PER_SITE = 50
LIMIT_NUMBER_OF_POST_PER_SLUG = 1000
LIMIT_NUMBER_OF_RECENT_POSTS = 1000
ARCHIVED_TIMESTAMP = 1672531200

def rebuild_sites():
    data = load_json("./blogs.json")[0] # English only now

    all_sites = []
    for category in data.get("categories", []):
        category_title = category.get("title", "")
        category_slug = category.get("slug", "")
        
        sites = category.get("sites", [])
        for site in sites:
            if site["site_url"] in UNSUPPORTED_SITE_URLS:
                continue
            site_dict = {
                "title": site.get("title", ""),
                "site_url": site.get("site_url", ""),
                "feed_url": site.get("feed_url", ""),
                # "category": category_title,
                "slug": category_slug
            }
            all_sites.append(site_dict)

    sites_json = {
        "updated": current_timestamp(),
        "sites": all_sites
    }
    save_json(sites_json, "sites.json")

    return all_sites

def parse_feed(site):
    site_url = site["site_url"]
    feed_url = site["feed_url"]

    if site_url in UNSUPPORTED_SITE_URLS:
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
            "site_url": site_url,
            "slug": site["slug"]
        }
        posts.append(post_dict)

    return posts

def generate_posts_by_sites(sites):
    with open('log_error_site.txt', 'w') as log_file:
        for site in sites:
            try:
                output_file_path = "./posts/by_site/" + simplifized_url(site["site_url"]) + ".json"
                print(f"processing {output_file_path}")

                if IS_DEBUG and os.path.isfile(output_file_path):
                    print(f"[debug] Skipped: {output_file_path}")
                    cached_posts_info = load_json(output_file_path)
                    posts = cached_posts_info["posts"]
                    timestamp = cached_posts_info["updated"]
                else:
                    posts = parse_feed(site)
                
                if not posts:
                    raise Exception("empty posts")
                else:
                    posts.sort(reverse=True, key=lambda t: t["updated"])

                    if not timestamp:
                        timestamp = current_timestamp()

                    posts_result = {
                        "updated": timestamp,
                        "posts": posts
                    }
                    save_json(posts_result, output_file_path)

                    # log timestamp
                    # timestamp = posts[0]['updated']
                    # log_file.write(f"{site['site_url']}, {len(posts)}, {timestamp}\n")

            except Exception as e:
                print(f"❌ Error parsing, {site['site_url']}, error: {str(e)}")
                log_file.write(f"{site['site_url']}\n")

def generate_posts_by_slugs(sites):
    for slug in SUPPORTED_SLUGS:
        slug_posts = []
        for site in sites:
            file_path = "./posts/by_site/" + simplifized_url(site["site_url"]) + ".json"
            if not site["slug"] == slug or not os.path.isfile(file_path):
                continue

            site_posts = load_json(file_path)["posts"]
            site_posts = list(filter(lambda t: (t["updated"] > ARCHIVED_TIMESTAMP), site_posts))
            site_posts = site_posts[slice(LIMIT_NUMBER_OF_POST_PER_SITE)]
            
            for post in site_posts:
                # Avoid duplicated post_id
                if any(filter(lambda p: p["id"] == post["id"], slug_posts)):
                    print(f"❌ > Duplicated post_id: {post['id']}")
                    continue
                slug_posts.append(post)
        
        slug_posts.sort(reverse=True, key=lambda t: t["updated"])
        slug_posts = slug_posts[slice(LIMIT_NUMBER_OF_POST_PER_SLUG)]

        slug_posts_result = {
            "updated": current_timestamp(),
            "posts": slug_posts
        }

        output_file_path = "./posts/by_slug/" + slug + ".json"
        save_json(slug_posts_result, output_file_path)
        print(f"+ slug {slug}: {len(slug_posts)}")


def generate_recent_posts():
    all_posts = []
    for slug in SUPPORTED_SLUGS:
        input_file_path = "./posts/by_slug/" + slug + ".json"
        if not os.path.isfile(input_file_path):
            print(f"❌ Slug posts not found: {slug}")
            continue
        slug_posts = load_json(input_file_path)["posts"]
        for post in slug_posts:
            # Avoid duplicated post_id since some site are included in more than 1 slug
            if any(filter(lambda p: p["id"] == post["id"], all_posts)):
                print(f"❌ > Duplicated post_id: {post['id']}")
                continue
            all_posts.append(post)

    all_posts.sort(reverse=True, key=lambda t: t["updated"])
    all_posts = all_posts[slice(LIMIT_NUMBER_OF_RECENT_POSTS)]

    all_posts_result = {
        "updated": current_timestamp(),
        "posts": all_posts
    }
    save_json(all_posts_result, "./posts/recent_posts.json")
    print(f"> Recent posts: {len(all_posts)}")


# main 

# 1. Download blogs json file from github repo
blogs = load_json_from_url("https://raw.githubusercontent.com/daveverwer/iOSDevDirectory/main/blogs.json")
save_json(blogs, "blogs.json")

# 2. Generate `sites.json` - array of Site
sites = rebuild_sites()

# 3. Generate `posts/by_site/{simplifized_site_url}_posts.json`s
# TODO: multithread this method
generate_posts_by_sites(sites)

# 4. Generate `posts/by_slug/{slug}.json}
generate_posts_by_slugs(sites)

# 5. TODO Get new posts for notification

# 6. Get recent posts 
generate_recent_posts()

# print(all_feeds)

# Sort by updated and save to `feeds.json`
# all_feeds.sort(reverse = True, key = lambda feed: feed["updated"])
# feeds_json = {
#     "updated": current_timestamp(),
#     "feeds": all_feeds
# }
# save_json(feeds_json, "feeds.json")