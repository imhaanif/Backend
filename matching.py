# import django
import django

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

import time
from df import face_verify
from textdistance import levenshtein
from django.db.models import Q
from core.models import Image, Item, Config, Match, Notification


class MatchItem:
    def __init__(self, item) -> None:
        try:
            c = Config.objects.all()[0]

            lev_threshold = c.lev_score_threshold
            face_threshold = c.face_match_threshold
        except Exception as e:
            print("config is missing")

        self.item = item
        self.matching_score = 0
        self.lev_threshold = lev_threshold
        self.image_threshold = face_threshold

    def location_match(self, data):
        if (
            self.item.main_cat.lower() == "persons"
            and self.item.sub_cat.lower() == "parents / sons"
        ):
            if data.get("state", "").lower() != self.item.data.get("state", "").lower():
                print("not matched")
                return False
            return True
        if (
            self.item.main_cat.lower() == "persons"
            and self.item.sub_cat.lower() == "missing person"
        ):
            return True

        if (
            data.get("place", "") == "public-place"
            or data.get("place", "") == "specific-place"
        ):
            # compare exact state
            if data.get("state", "").lower() != self.item.data.get("state", "").lower():
                print("not matched")
                return False

            # IF CATEOGORY IS WALLET OR CARD DOCS

            if (
                self.item.data["main_cat"].lower() == "wallet"
                or self.item.data["main_cat"].lower() == "card & official documents"
            ):
                return True

            else:
                print("state matched")
                print("matching for city")
                # compare city
                if data.get("city", "").lower() != self.item.city.lower():
                    print("not matched")
                    return False
                else:
                    print("city matched")
                    return True
        elif data.get("place", "") == "state":
            if data.get("state", "") != self.item.data.get("state", ""):
                print("not matched")
                return False
            else:
                print("state matched")
                if data.get("item-car-type", "") != self.item.data.get(
                    "item-car-type", ""
                ):
                    print("car type not matched")
                    return False
                else:
                    print("car type matched")
                    return True

        elif data.get("place", "") == "interstate":
            print("interstate")
            if data.get("departure-state", "") != self.item.data.get(
                "departure-state", ""
            ):
                print("departure state not matched matched")
                return False
            else:
                print("departure state matched")
                if data.get("item-car-type", "") != self.item.data.get(
                    "item-car-type", ""
                ):
                    print("car type not matched matched")
                    return False
                else:
                    print("car type matched")
                    return True
                # if data['arrival-state'] != self.item.data['arrival-state']:
                #     print("arrival state not matched matched")
                #     return False
                # else:
                #     print("arrival state also matched")

    def wallet(self, data):
        if self.item.data.get("color", "") != data.get("color", ""):
            return False
        else:
            name_l = levenshtein.normalized_similarity(
                self.item.data.get("name", ""), data.get("name", "")
            )
            fm_l = levenshtein.normalized_similarity(
                self.item.data.get("family_name", ""), data.get("family_name", "")
            )
            result = max(name_l, fm_l)
            matching_score = (0.5 + 0.5 * result) * 100
            print(matching_score, "matching_score")
            self.matching_score = matching_score
            if matching_score >= self.lev_threshold:
                return True
            else:
                return False

    def electronics(self, data):
        if self.item.data.get("brand", "") != data.get("brand", ""):
            return False
        elif self.item.data.get("color", "") != data.get("color", ""):
            return False
        return True

    def key(self, data):
        if self.item.data.get("key_type", "") != data.get("key_type", ""):
            return False
        elif self.item.data.get("key_number", "") != data.get("key_number", ""):
            return False
        return True

    def watch(self, data):
        if self.item.data.get("watch_type", "") != data.get("watch_type", ""):
            return False
        elif self.item.data.get("color", "") != data.get("color", ""):
            return False
        return True

    def jewlery(self, data):
        if self.item.data.get("jewelery_type", "") != data.get("jewelery_type", ""):
            return False
        elif self.item.data.get("metal", "") != data.get("metal", ""):
            return False
        return True

    def money(self, data):
        if self.item.data.get("money_amount", "") != data.get("money_amount", ""):
            return False

        return True

    def glasses(self, data):
        if self.item.data.get("glasses_type", "") != data.get("glasses_type", ""):
            return False
        elif self.item.data.get("color", "") != data.get("color", ""):
            return False
        return True

    def card_and_docs(self, data):
        if self.item.data.get("sex", "") != data.get("sex", ""):
            return False
        else:
            name_l = levenshtein.normalized_similarity(
                self.item.data.get("name", ""), data.get("name", "")
            )
            fm_l = levenshtein.normalized_similarity(
                self.item.data.get("family_name", ""), data.get("family_name", "")
            )
            result = max(name_l, fm_l)
            matching_score = (0.5 + 0.5 * result) * 100
            print(matching_score, "matching_score")
            self.matching_score = matching_score
            if matching_score >= self.lev_threshold:
                return True
            else:
                return False

    def bag_and_luggage(self, data):
        if self.item.data.get("color", "") != data.get("color", ""):
            return False
        else:
            return True

    def animals(self, data):
        if self.item.data.get("animal_color", "") != data.get("animal_color", ""):
            return False
        return True

    def persons(self, data):
        if self.item.data.get("sex", "") != data.get("sex", ""):
            return False
        elif self.item.data.get("age_cat", "") != data.get("age_cat", ""):
            return False

        else:
            name_l = levenshtein.normalized_similarity(
                self.item.data.get("name", ""), data.get("name", "")
            )
            fm_l = levenshtein.normalized_similarity(
                self.item.data.get("family_name", ""), data.get("family_name", "")
            )
            result = max(name_l, fm_l)
            matching_score = (0.5 + 0.5 * result) * 100
            print(matching_score, "matching_score")
            self.matching_score = matching_score
            if matching_score >= self.lev_threshold:
                return True
            else:
                return False

    def parent_son(self, data):
        if self.item.data.get("child_sex", "") != data.get("child_sex", ""):
            return False
        elif self.item.data.get("birthday", "") != data.get("birthday", ""):
            return False

        # elif self.item.data['mental_state'] != data['mental_state']:
        #     return False
        else:
            f_name = levenshtein.normalized_similarity(
                self.item.data.get("father_name", ""), data.get("father_name", "")
            )
            ff_name = levenshtein.normalized_similarity(
                self.item.data.get("father_family_name", ""),
                data.get("father_family_name", ""),
            )
            m_name = levenshtein.normalized_similarity(
                self.item.data.get("mother_name", ""), data.get("mother_name", "")
            )

            mf_name = levenshtein.normalized_similarity(
                self.item.data.get("mother_family_name", ""),
                data.get("mother_family_name", ""),
            )

            s_name = levenshtein.normalized_similarity(
                self.item.data.get("son_name", ""), data.get("son_name", "")
            )
            result = max(f_name, ff_name, m_name, mf_name, s_name)

            matching_score = (0.5 + 0.5 * result) * 100
            print(matching_score, "matching_score")
            self.matching_score = matching_score
            if matching_score >= self.lev_threshold:
                return True
            else:
                return False

    def lost_item_matching(self):
        print("matching for lost item")
        items = Item.objects.filter(
            state="found",
            main_cat=self.item.main_cat,
            sub_cat=self.item.sub_cat,
            country=self.item.country,
            status="search",
        ).order_by("-created_at")
        print("all items", len(items))
        items = items.exclude(matched_with__in=[self.item])
        print("after excluding with already matched in", len(items))

        for item in items:
            self.match_data(item)
            self.item.matched_with.add(item)
            self.item.save()

    def create_match(self, item, res=None):
        self.create_notifications(item, self.item)

        if item.state == "lost":
            lost_item = item
            found_item = self.item
        else:
            lost_item = self.item
            found_item = item
        if res is None:
            Match.objects.create(
                found_item=found_item,
                lost_item=lost_item,
                matching_score=self.matching_score,
                face_matching_data={
                    "is_face_compared": False,
                },
            )

            self.item.status = "match"
            self.item.save()
            item.status = "match"
            item.save()
        else:
            Match.objects.create(
                found_item=found_item,
                lost_item=lost_item,
                matching_score=self.matching_score,
                image_score=res["distance"],
                face_matching_data=res,
            )

            self.item.status = "match"
            self.item.save()
            item.status = "match"
            item.save()

    def match_data(self, item):
        data = item.data

        ##data is the item is compared to
        print(data)
        # if self.item.main_cat != "persons":

        if not self.location_match(data):
            return
        else:
            print("location matched")
            if self.item.main_cat == "card & official documents":
                myfunc = self.card_and_docs
            elif self.item.main_cat == "electronics":
                myfunc = self.electronics

            elif self.item.main_cat == "wallet":
                myfunc = self.wallet
            elif self.item.main_cat == "personal stuff":
                if self.item.sub_cat == "key":
                    myfunc = self.key
                elif self.item.sub_cat == "hand watch":
                    myfunc = self.watch
                elif self.item.sub_cat == "glasses":
                    myfunc = self.glasses
                elif self.item.sub_cat == "jewelery":
                    myfunc = self.jewlery
                elif self.item.sub_cat == "money":
                    myfunc = self.money
            elif self.item.main_cat == "bag & luggage":
                myfunc = self.bag_and_luggage
            elif self.item.main_cat == "animals":
                myfunc = self.animals
            elif self.item.main_cat == "persons":
                if self.item.sub_cat == "missing person":
                    myfunc = self.persons
                elif self.item.sub_cat == "parents / sons":
                    myfunc = self.parent_son

            print("calling function Now")

            if (
                self.item.main_cat.lower() == "persons"
                and self.item.sub_cat.lower() == "missing person"
            ):
                if myfunc(data):
                    # match item not need to match images
                    self.create_match(item)
                    return

                else:
                    print("not matched but matching images")

                    if self.item.images.all().count() > 1:
                        lost_image = self.item.images.first().image.path

                    else:
                        lost_image = None
                        print("no images for lost item")

                    if item.images.all().count() > 1:
                        found_image = item.images.first().image.path
                    else:
                        found_image = None
                        print("no images for found item")

                    print(lost_image, found_image, "image paths")
                    if lost_image and found_image:
                        try:
                            res = face_verify(lost_image, found_image)
                            print(res)

                            if res["verified"] == True:
                                self.create_match(item, res)
                                return

                        except Exception as e:
                            print(e)

                            return
                    else:
                        print("not match found")
                        return
            if myfunc(data):
                self.create_match(item, res=None)
                return

    def create_notifications(self, item1, item2):
        if item1.state == "lost":
            lost_item = item1
            found_item = item2
        else:
            lost_item = item2
            found_item = item1
        Notification.objects.create(
            user=lost_item.user,
            data={
                "item_id": lost_item.id,
            },
            msg="Your item has been matched with a found item",
        )
        Notification.objects.create(
            user=found_item.user,
            data={
                "item_id": found_item.id,
            },
            msg="Your item has been matched with a lost item",
        )

    def found_item_matching(self):
        print("matching for found item")
        items = Item.objects.filter(
            state="lost",
            main_cat=self.item.main_cat,
            sub_cat=self.item.sub_cat,
            country=self.item.country,
            status="search",
        ).order_by("-created_at")
        print("all items", len(items))
        items = items.exclude(matched_with__in=[self.item])
        print("after exceluding with already matched in", len(items))

        for item in items:
            self.match_data(item)
            self.item.matched_with.add(item)
            self.item.save()

    def match(self):
        if self.item.state == "lost":
            self.lost_item_matching()
        else:
            self.found_item_matching()


def match_main():
    for item in Item.objects.filter(status="search"):
        print(item.id)
        match = MatchItem(item)
        match.match()


if __name__ == "__main__":
    match_main()
