from _CONSTANTS import WEBDRIVER_PATH, USERNAME, PASSWORD, MONGO_DB_PATH, MONGO_DB_NAME
from InstagramSession import InstagramSession
import logging

########################################################################################################################
logging.basicConfig(#filename = 'harry.log',
                    level=logging.INFO,
                    format='%(levelname)s\t%(asctime)s\t%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
self = InstagramSession(WEBDRIVER_PATH, USERNAME, PASSWORD, MONGO_DB_PATH, MONGO_DB_NAME)
########################################################################################################################
# TESTING
# InstaPage
self.page.cst_login(USERNAME, PASSWORD)

# InstaSession
self.cst_scrape_profiles("", max_num_profiles=5) # ok
self.cst_scrape_profiles_info(test=False, method="direct", direct_profile="") #ok
self.cst_scrape_posts(max_num_posts=25, query={"profile": ""}, profile_limit=None, test=False) #ok
self.cst_scrape_post_info(query={"profile": ""}, posts_limit=10, test=False)

########################################################################################################################
# ANALYZE


########################################################################################################################
# DEVELOPING

########################################################################################################################
# DEBUG

########################################################################################################################
# REMEDIATION
