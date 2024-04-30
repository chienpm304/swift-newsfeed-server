

blogs: [
    {
        lang
        categories: [
            {
                slug
                sites: [ { id, title, link, updated } ]
            }
        ]
    }
]

# Milestones
## Stage 1: Barebone happy case
- No authentication for server side, app use fake auth.
- Supports English category only.
- Hardcodes all static info like slugs, english only.
- Limits the num of posts for each post-json files to 100.
- No paging support from server, app can consider paging it own.
- Sever 
- Use 



# Features
0. Predefine:
- Handle Enligh category only, which result in:
- All supported slugs: `development, updates, packages, design, marketing, companies, podcasts, newsletters, youtube, twitch`

1. Get recently posts from all supported slug:
- Return the most recently posts from all supported slugs
- Using `Post.updated` (timestamp) field to determine the order, the higher value
- Server to prepare recently posts json data named `latest_posts.json`:
    + Json structure:
        ```json
        {
            "updated": int64, /* timestamp */
            "posts": [/* List of Post */]
        }
        ```
    + Due to the huge number records for some slug, limit the number of records to 200
    + The number of posts will be fixed, using LIFO strategy to add/remove post


2. Get Posts by Site
- Server to preparse `Post`s by `Site` json for client.
- Json files in `posts/by_site/{simplifized_site_url}.json`:
    + `Site`'s primary key is `site_url`, let use this for routing resources.
    + Simplifized a `site_url` is needed because we need to pass the url arround, so making it simplized will have a ton of benefits.
    + `simplifized_url` should be synced between serve and client, where we simply replace all `non digits and non alphabet character` by `_` from `site_url` (which is the Site's primary key!)
        Python
        ```python
        def simplifized_url(stringUrl):
            prefixes = ["http://www.", "https://www.", "http://", "https://"]
            for prefix in prefixes:
                if stringUrl.startswith(prefix):
                    stringUrl = stringUrl[len(prefix):]
            return re.sub(r'[^a-zA-Z0-9]', '_', stringUrl)
        ```
        Swift
        ```swift
        func simplifiedURL(_ stringURL: String) -> String {
            let prefixes = ["http://www.", "https://www.", "http://", "https://"]
            var stringURL = stringURL
            
            for prefix in prefixes {
                if stringURL.hasPrefix(prefix) {
                    stringURL = String(stringURL.dropFirst(prefix.count))
                }
            }
            
            return stringURL.replacingOccurrences(of: "[^a-zA-Z0-9]", with: "_", options: .regularExpression)
        }

        ```
    + Json format:
        ```json
        {
            "updated": int64, /* timestamp */
            "posts": [/* List of Post */]
        }
        ```


3. Get Posts by Category (slug)
- Return a list of posts belongs to given slug
- Server to prepare posts by slugs in `posts/by_slug/{slug}.json`:
    + Json format:
        ```json
        {
            "updated": int64, /* timestamp */
            "posts": [/* List of Post */]
        }
        ```
- Because a `Category` contains `Site`s, we can compute all `Post`s belongs a `Category` by combining all `Post`s of `Site`s that belongs to the `Category`.
- Due to the huge number records for some slug, consider to limit the number of records, e.g: 100 / 200 records
    + TODO: check the data to get insight later


4. Notify new post / post updated:
- When the `Data update mechanism` get done, we absolute can get new `posts` based on json snapshots's `updated` filed.
- Store the new posts in a json named `new_posts.json`
- Json structure:
    ```json
        {
            "updated": int64, // timestamp
            "posts": /* [Post] */
        }
    ```
- Using a third party / online service to get the `new_posts.json` and send APNS request to app. 

5. Get all sites info:
- Return list of `Site`s, which we recomputed from `categories.json`
- Json file path `sites.json`:
    ```json
        [
            {
                "title": "Kodeco Podcast",
                "site_url": "https://www.kodeco.com/podcast/",
                "feed_url": "https://www.kodeco.com:443/feed/podcast",
                "category": "Development or Design Podcasts",
                "slug": "podcasts"
            },
            // ...
        ]
    ```

6. Get sites by slug:
- App to fetch the `categories.json` and filter out sites by slug.


(*). Data update mechanism:
- The thumb of rule: to keep the server simplication - using json based as server
- Manually run the script to update the data, include:
    + Update the latest categories from [Github repo](https://raw.githubusercontent.com/daveverwer/iOSDevDirectory/main/blogs.json)
    + Generate `sites.json`
    + Loops through all sites, parse the `feed_url` and generte `posts by sites` jsons.
    + Computes `{slug_posts.json}` from posts by site


# App Models
```swift
struct Category {
    let slug: String // PK
    let title: String 
    let description: String
}

struct Site {
    let site_url: String // PK
    let title: String
    let author: String
    let feed_url: String
    let category_slug: String // FK (Category)
}

struct Post {
    let id: String // PK
    let title: String 
    let link: String 
    let updated: int64 // Timestamp
    let site_url: String // FK (Site)
}
```