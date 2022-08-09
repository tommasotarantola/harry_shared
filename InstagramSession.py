from InstagramPage import InstagramPage
from InstaMongoDB import InstaMongoDB
import logging


class InstagramSession:
    def __init__(self, driver_path, username, password, db_path, db_name):
        self.mongodb = InstaMongoDB(db_path, db_name)
        self.page = InstagramPage(driver_path, username, password)
        self.logger = logging.getLogger()

    def cst_scrape_profiles(self, seed_profile: str, max_num_profiles: int):
        self.logger.info(f"Starting scraping profiles from: {seed_profile}")
        profile_list = self.page.cst_get_profiles(seed_profile, max_num_profiles)
        self.mongodb.cst_insert_profiles(profile_list)
        self.logger.info(f"Ending scraping profiles from: {seed_profile}")

    def cst_scrape_profiles_info(self, test=False, method="db", direct_profile=None):
        if method == "db":
            self.logger.info(f"Starting scraping info for not checked profiles")
            profile_list = self.mongodb.cst_mongo_find("all_profiles",
                                                       {"to_check": True},
                                                       {"profile": 1})
        elif method == "direct":
            self.logger.info(f"Starting scraping info for not checked profiles")
            profile_list = [{"profile": direct_profile}]
        self.logger.info(f"Founded {len(profile_list)} profiles")
        profile_info_list = []
        if not test:
            for profile_dict in profile_list:
                profile = profile_dict["profile"]
                try:
                    profile_info = self.page.cst_get_profile_info(profile)
                    profile_info_list.append(profile_info)
                except Exception as error:
                    self.logger.error(f"Error in scraping {profile} info: {error}")
            self.mongodb.cst_update_profiles(profile_info_list)
        self.logger.info(f"Ending scraping info for not checked profiles. "
                         f"Scraped {len(profile_info_list)} profiles")

    def cst_scrape_posts(self, max_num_posts, query={"to_check_posts": True}, profile_limit=None, test=False):
        self.logger.info(f"Starting scraping posts from not checked profiles")
        profile_list = self.mongodb.cst_mongo_find("all_profiles",
                                                   query,
                                                   {"profile": 1}, limit=profile_limit)
        self.logger.info(f"Founded {len(profile_list)} profiles.")
        tot_post = 0
        if not test:
            for profile in self.mongodb.cst_flat_dict(profile_list, "profile"):
                self.logger.info(f"Starting scraping post from: {profile}")
                post_list = self.page.cst_get_posts(profile, max_num_post=max_num_posts)
                self.mongodb.cst_insert_posts(post_list)
                num_scraped_posts = self.mongodb.cst_mongo_find("all_posts", {"profile": profile})
                tot_post = tot_post + len(post_list or [])
                self.mongodb.cst_mongo_update("all_profiles",
                                              {"profile": profile},
                                              {"$set": {"to_check_posts": False,
                                                        "num_scraped_posts": num_scraped_posts}})
                self.logger.info(f"Ending scraping post from: {profile}")
        self.logger.info(f"Ending scraping profiles from not checked profiles."
                         f"Scraped {len(profile_list)} profiles, founded {tot_post} posts")

    def cst_scrape_post_info(self, query={"to_check": True}, posts_limit=None, test=False):
        self.logger.info(f"Starting scraping posts from not checked posts")
        post_list = self.mongodb.cst_mongo_find("all_posts",
                                                   query,
                                                   {"profile": 1, "post": 1},
                                                   limit=posts_limit)
        self.logger.info(f"Founded {len(post_list)} posts.")
        post_info_list = []
        if not test:
            for post_dict in post_list:
                profile = post_dict["profile"]
                post = post_dict["post"]
                self.logger.info(f"Strating scraping from {profile}: {post}")
                try:
                    post_info = self.page.cst_get_post_info(post, max_number_likes=1000)
                    post_info_list.append(post_info)
                except Exception as error:
                    self.logger.error(f"Error in scraping info from {profile} - {post}: {error}")
            self.mongodb.cst_update_post(post_info_list)
        self.logger.info(f"Ending scraping info for not checked posts. "
                         f"Scraped {len(post_info_list)} posts")

