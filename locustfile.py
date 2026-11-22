import random
from locust import HttpUser, task, between


class ShopUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task(8)
    def get_hot_item(self):
        self.client.get("/items/item0", name="/items/hot")

    @task(2)
    def get_random_item(self):
        number = random.randint(0, 999)
        self.client.get(f"/items/item{number}", name="/items/random")


class LockedShopUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task(8)
    def get_hot_item(self):
        self.client.get("/items-locked/item0", name="/items-locked/hot")

    @task(2)
    def get_random_item(self):
        number = random.randint(0, 999)
        self.client.get(f"/items-locked/item{number}", name="/items-locked/random")
