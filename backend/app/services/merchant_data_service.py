from backend.app.models.merchant_policy import MerchantPolicy
from pathlib import Path
import csv


DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class MerchantDataService:

    def __init__(self):
        self.merchants = self._load_csv("merchants.csv")
        self.products = self._load_csv("products.csv")
        self.inventory = self._load_csv("inventory.csv")
        self.delivery_options = self._load_csv("delivery_options.csv")
        self.offers = self._load_csv("offers.csv")
        self.policies = self._load_csv("policies.csv")

    def _load_csv(self, filename):
        file_path = DATA_DIR / filename

        with open(
            file_path,
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            return list(csv.DictReader(file))

    def get_all_products(self):
        return self.products

    def get_product(self, product_id):
        for product in self.products:
            if product["product_id"] == product_id:
                return product

        return None

    def get_inventory(self, product_id):
        for item in self.inventory:
            if item["product_id"] == product_id:
                return item

        return None

    def get_delivery_options(self, product_id):
        for option in self.delivery_options:
            if option["product_id"] == product_id:
                return option

        return None

    def get_active_offers(self, product_id=None):
        active_offers = [
            offer
            for offer in self.offers
            if offer["active"].lower() == "true"
        ]

        if product_id:
            active_offers = [
                offer
                for offer in active_offers
                if offer["product_id"] == product_id
            ]

        return active_offers

    def get_merchant_policy(self, merchant_id):
        for policy in self.policies:
            if policy["merchant_id"] == merchant_id:
                return policy

        return None

    def get_merchant_policy_model(self, merchant_id):
        policy = self.get_merchant_policy(merchant_id)

        if policy is None:
            return None

        allowed_actions = []

        if policy["allow_product_substitution"].lower() == "true":
            allowed_actions.append("substitute_product")

        if policy["allow_payment_retry"].lower() == "true":
            allowed_actions.append("payment_retry")

        if policy.get("allow_offer_incentive", "false").lower() == "true":
            allowed_actions.append("offer_incentive")

        if policy.get("allow_delivery_change", "false").lower() == "true":
            allowed_actions.append("change_delivery")

        return MerchantPolicy(
            max_discount_percent=float(
                policy["max_discount_percent"]
            ),
            max_incentive_amount=float(
                policy.get("max_incentive_amount", 500)
            ),
            min_margin_percent=float(
                policy["min_margin_percent"]
            ),
            allow_product_substitution=(
                policy["allow_product_substitution"].lower() == "true"
            ),
            allow_payment_retry=(
                policy["allow_payment_retry"].lower() == "true"
            ),
            max_payment_retries=int(
                policy["max_payment_retries"]
            ),
            allowed_actions=allowed_actions,
            allow_escalation=True,
            max_automated_attempts=3,
            minimum_expected_recovery_value=100.0,
        )

    def get_merchant(self, merchant_id):
        for merchant in self.merchants:
            if merchant["merchant_id"] == merchant_id:
                return merchant

        return None
