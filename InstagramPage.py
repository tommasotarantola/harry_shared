from ChromePage import ChromePage
import logging
import re
from _INSTAGRAM_MAP import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime as dt
import pytz

POST_Comment_List = "._a9zr"

class InstagramPage(ChromePage):
    def __init__(self, driver_path, username, password):
        ChromePage.__init__(self, driver_path)
        self.user_profile = username
        self.user_logged = False
        self.utc = pytz.UTC
        self.cst_login(username, password)
        self.logger = logging.getLogger()

    @staticmethod
    def cst_real_number(num_string):
        num_string = re.findall("[0-9a-zA-Z,\.]+", str(num_string))[0]
        num_string = num_string.replace(",", "")
        if bool(re.search("[kK]", num_string)):
            num_string = re.sub("[kK]", "", num_string)
            return int(float(num_string) * 1000)
        elif bool(re.search("[mM]", num_string)):
            num_string = re.sub("[mM]", "", num_string)
            return int(float(num_string) * 1000 * 1000)
        else:
            return int(num_string)

    # Check if the current page is the correct one
    def cst_check_isprofile(self, profile):
        if self.current_url.find(profile) < 0:
            raise Exception("Not profile page")

    def cst_home(self):
        self.get("https://www.instagram.com/")

    def cst_clean(self, path: str, navigable=False):
        obj = path.removeprefix(HOMEPAGE)
        obj = re.sub("/+$", "", obj)
        if navigable:
            obj = HOMEPAGE + obj + "/"
        return obj

    def cst_navigate_obj(self, obj):
        obj = self.cst_clean(obj, navigable=True)
        logging.info(f"Navigation: {obj}")
        self.get(obj)

        self.cst_wait(3, 1, 2)
        page_available = True
        try:
            unavailable = self.cst_find_elements(page_unavailable)[0]
            if unavailable.text.find("Sorry, this page isn't available") >= 0:
                page_available = False
        except:
            pass
        if not page_available:
            raise Exception("Page unavailable")

    # SCRAPING OBJS
    def cst_get_profiles(self, seed_profile, max_num_profiles):
        ''''Return follower profiles of the seed profiles, number_profiles specifies the max number'''
        logging.info(f"Retrieve profiles start: from: {seed_profile} until: {max_num_profiles}")
        self.cst_navigate_obj(seed_profile)
        # Click on followers button
        self.cst_find_elements(PROFILE_InfoTabList)[1].click()
        self.cst_wait()
        # Define extraction function on web element and extract followers
        def x(elem):
            return elem.get_attribute("href")
        followers = self.cst_load_retrieve_parse(POPUP_Followers_ProfileList,
                                                 until=max_num_profiles,
                                                 parse_function=x,
                                                 scroll_method="web_element")
        self.back()
        profile_list = [{"profile": self.cst_clean(f)} for f in followers]
        logging.info(f"Retrieve profiles success: retrieved {len(followers)} profiles")
        return profile_list

    def cst_get_posts(self, profile, max_num_post):
        self.logger.info(f"Retrieve posts start: from: {profile} until: {max_num_post}")
        self.cst_navigate_obj(profile)
        profile_post_list = None
        # Define extraction function on found web element and extract posts
        try:
            posts = self.cst_load_retrieve_parse(PROFILE_POST_LINK_LIST,
                                                 until=max_num_post,
                                                 parse_function=lambda x: x.get_attribute("href"),
                                                 scroll_method="page")
        except Exception as error:
            self.logger.error(f"Error in searching {profile} posts: {error}")
            self.logger.info(f"Retrieve posts not success: posts not founded")
            return None
        profile_post_list = [{
            "profile": self.cst_clean(profile),
            "post": self.cst_clean(post)} for post in posts]
        self.logger.info(f"Retrieve posts success: retrieved {len(posts)} posts")

        return profile_post_list

    # SCRAPING OBJ INFO
    def cst_get_profile_info(self, profile, account_private_delay=1):
        self.cst_navigate_obj(profile)
        profile_info = self.cst_find_elements(PROFILE_InfoTabList)
        post_num = self.cst_real_number(profile_info[0].text)
        follower_num = self.cst_real_number(profile_info[1].text)
        following_num = self.cst_real_number(profile_info[2].text)
        public = None
        description = self.cst_find_elements(profile_description_text)[0].text

        # Check if find "This account is private" string
        try:
            private = self.cst_find_elements(account_private_text, delay=account_private_delay, log=False)
            if private[0].text.lower().find("private") >= 0:
                public = False
            else:
                public = None
        except:
            public = True
        profile_info = {
            "profile": self.cst_clean(profile),
            "post_num": post_num,
            "follower_num": follower_num,
            "following_num": following_num,
            "public": public,
            "description": description,
            "lud": dt.datetime.now(dt.timezone.utc),
            "to_check": False
        }
        logging.info(f"Retrieved_info success: {profile}")
        return profile_info

    def cst_get_post_info(self, post, max_number_likes):
        logging.info(f"Retrieve post info start: {post}")
        self.cst_navigate_obj(post)
        self.cst_wait()
        now = dt.datetime.now(dt.timezone.utc)
        profile = self.cst_find_elements(profile_text)[0].text
        try:
            photo_description = self.cst_find_elements(photo_description_text)[0].get_attribute("alt")
        except Exception as error:
            logging.error(f"Error in finding photo_description: {error}")
            photo_description = None
        iso_date = self.cst_find_elements(POST_DATE_TEXT)[0].get_attribute("datetime")
        post_date = self.utc.localize(dt.datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ"))
        # Extract likes
        try:
            liked_button = self.cst_find_elements(post_liked_by_others)[0]
            liked_button.click()
            liked_by_profiles = self.cst_load_retrieve_parse(post_liked_popup_profile_list,
                                                             until=max_number_likes,
                                                             parse_function= lambda x: x.text,
                                                             scroll_method="web_element")
            if len(liked_by_profiles) == max_number_likes:
                number_likes = "+" + str(len(liked_by_profiles))
            elif len(liked_by_profiles) < max_number_likes:
                number_likes = len(liked_by_profiles)
            else:
                number_likes = None
            self.cst_send_keys(Keys.ESCAPE)
        except Exception as error:
            number_likes = None
            liked_by_profiles = None
            self.logger.error(f"Error in finding likes: {error}")
        # Extract comments
        try:
            we_comments = self.cst_find_elements(POST_Comment_List)
            comments = []
            for we_comment in we_comments:
                comment_profile = we_comment.find_element(By.CSS_SELECTOR, "span._aap6._aap7._aap8 a").text
                comment_description = we_comment.find_element(By.CSS_SELECTOR, "div._a9zs").text
                comment = {
                    "comment_profile": comment_profile,
                    "comment_description": comment_description}
                comments.append(comment)
        except Exception as error:
            comments = None
            self.logger.error(f"Error in finding comments: {error}")
        # Check post is stable
        delta = dt.timedelta(hours=72)
        if now > post_date + delta:  to_check = False
        else: to_check = True

        profile_post_info = {
            "profile": self.cst_clean(profile),
            "post": self.cst_clean(post),
            "photo_description": photo_description,
            "post_date": post_date,
            "number_likes": number_likes,
            "liked_by_profiles": liked_by_profiles,
            "comments": comments,
            "lud": now,
            "to_check": to_check
        }
        logging.info(f"Retrieve post info success from {profile}: {post}")
        return profile_post_info

    ####################################################################################################################
    # ACTIONS

    # Login to site
    def cst_login(self, username, password):
        logging.info("Login start")
        if self.user_logged:
            logging.info("Login success: user already logged")
            return True
        else:
            try:
                # Navigate instagram
                self.get("https://www.instagram.com/accounts/login/")
                self.cst_wait(4, 1, 3)
                # Accept cookies
                self.cst_click(".bIiDR")
                self.cst_wait(4, 1, 3)
                # Login
                self.cst_write(username, ".zyHYP", position=0)
                self.cst_write(password, ".zyHYP", position=1)
                self.cst_click(".DhRcB")
                self.cst_wait(4, 1, 3)
                # Not save login info
                # self.cst_click(POPUP_SaveInfo_NotNow)
                self.cst_wait(4, 1, 3)
                # Turn off notifications
                # self.cst_click(POPUP_TurnOnNotification_NotNowButton)
                # self.cst_wait()
                if self.current_url == "https://www.instagram.com/":
                    logging.info("Login success")
                    self.user_logged = True
                    return True
                else:
                    raise Exception("Something went wrong, home page not reached")
            except Exception as error:
                logging.error(f"Error in login: {error}")

    # Function to navigate and follow a profile
    def cst_follow_unfollow(self, profile, action):
        logging.info(f"Follow_unfollow start: {action} {profile}")
        self.cst_navigate_obj(profile)
        follow_button = self.cst_find_elements(profile_upper_buttons)[1]

        # Define status of profile
        if follow_button.text == "Follow":
            profile_followed = False
        elif follow_button.text == "":
            profile_followed = True
        else:
            raise Exception("Something went wrong: Follow button not found")

        # Action to take
        if action == "follow" and profile_followed:
            logging.info(f"Follow success: {profile} already followed")
            return False
        elif action == "follow" and not profile_followed:
            follow_button.click()
            logging.info(f"Follow success: {profile}")
            return True
        elif action == "unfollow" and profile_followed:
            follow_button.click()
            self.cst_wait()
            unfollow_popup = self.cst_find_elements(unfollow_popup_button_list)[0]
            if unfollow_popup.text == "Unfollow":
                unfollow_popup.click()
                logging.info(f"Unfollow success: {profile}")
                return True
            else:
                raise Exception("Something went wrong: Unfollow popup not found")
        elif action == "unfollow" and not profile_followed:
            logging.info(f"Unollow success: {profile} alraedy unfollow")
            return False
        else:
            raise Exception("Something went wrong: action not recognized?")

    # Function to navigate and like a post
    def cst_like_unlike(self, post, action):
        logging.info(f"Like_unlike start: {action} {post}")
        self.cst_navigate_obj(post)
        like_button = self.cst_find_elements(post_like_button)[0]

        # Define like unlike
        if like_button.get_attribute("aria-label") == "Unlike":
            post_liked = True
        elif like_button.get_attribute("aria-label") == "Like":
            post_liked = False
        else:
            raise Exception("Something went wrong: Like button not found")

        # Action to take
        if action == "like" and post_liked:
            logging.info(f"Like success: {post} already like")
            return False
        elif action == "like" and not post_liked:
            like_button.click()
            logging.info(f"Like success: {post}")
            return True
        elif action == "unlike" and post_liked:
            like_button.click()
            logging.info(f"Unlike success: {post}")
            return True
        elif action == "unlike" and not post_liked:
            logging.info(f"Unlike success: {post} already unlike")
            return False
        else:
            raise Exception("Something went wrong: action not recognized?")

    # Function to navigate and comment a post
    def cst_comment(self, post, comment):
        logging.info(f"Write comment start: {comment} on {post}")
        self.cst_navigate_obj(post)

        comment_panel = self.cst_find_elements("RxpZH", method="class")[0]
        text_box = comment_panel.find_element_by_css_selector(".Ypffh")
        post_button = comment_panel.find_element_by_css_selector(".yWX7d")

        text_box.send_keys(comment)
        self.cst_wait()

        if post_button.text == "Post":
            post_button.click()
            self.cst_wait()
            logging.info(f"Write comment success")
            return True
        else:
            raise Exception("Something went wrong: Post button not found")

