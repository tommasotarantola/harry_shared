from MongoDB import MongoDB
import logging
import datetime as dt


class InstaMongoDB(MongoDB):
    def __init__(self, db_path, db_name):
        self.logger = logging.getLogger()
        self.logger.info(f"Starting DB connection to {db_path} >> {db_name}")
        MongoDB.__init__(self, db_path, db_name)

    # ALL_PROFILES
    def cst_insert_profiles(self, profile_list):
        if not isinstance(profile_list, list): raise Exception("Profiles must be a list!")
        results = []
        matched = 0
        for profile in profile_list:
            result = self.db["all_profiles"].update_one(
                profile,
                {"$setOnInsert": {"to_check": True,
                                  "to_check_posts": True,
                                  "lud": dt.datetime.now(dt.timezone.utc)}},
                upsert=True
            )
            matched = matched + result.matched_count
            results.append(result)

        self.logger.info(f"Stored {len(profile_list) - matched} new profiles")
        return results

    def cst_update_profiles(self, profile_info_list):
        if not isinstance(profile_info_list, list): raise Exception("Profiles info must be a list!")
        results = []
        matched = 0
        for profile_info in profile_info_list:
            result = self.db["all_profiles"].update_one(
                {"profile": profile_info["profile"]},
                {"$set": profile_info},
                upsert=True)
            matched = matched + result.matched_count
            results.append(result)

        self.logger.info(f"Stored: {len(profile_info_list) - matched} new profiles, update: {matched} profiles ")
        return results

    # ALL_POSTS
    def cst_insert_posts(self, profile_post_list, update=None):
        results = []
        if profile_post_list is None:
            tot_matched = 0
        else:
            if not isinstance(profile_post_list, list): raise Exception("Posts must be a list!")
            matched = 0
            for profile_post in profile_post_list:
                result = self.db["all_posts"].update_one(
                    {"profile": profile_post["profile"],
                     "post": profile_post["post"]},
                    {"$setOnInsert": {"to_check": True,
                                      "lud": dt.datetime.now(dt.timezone.utc)}},
                    upsert=True
                )
                matched = matched + result.matched_count
                results.append(result)
            tot_matched = {len(profile_post_list) - matched}
        self.logger.info(f"Stored {tot_matched} new posts")
        return results

    def cst_update_post(self, profile_post_info_list):
        if not isinstance(profile_post_info_list, list): raise Exception("Posts info must be a list!")
        results = []
        matched = 0
        for profile_post_info in profile_post_info_list:
            result = self.db["all_posts"].update_one(
                {"profile": profile_post_info["profile"],
                 "post": profile_post_info["post"]},
                {"$set": profile_post_info},
                upsert=True
            )
            matched = matched + result.matched_count
            results.append(result)

        self.logger.info(f"Stored: {len(profile_post_info_list) - matched} new posts, update: {matched} posts ")
        return results


