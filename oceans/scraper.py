import sys
from typing import Union , ClassVar , Callable , Iterator , Iterable
import time
from abc import abstractmethod , ABC
import argparse
import pathlib
import os
from datetime import datetime , timedelta
from termcolor import colored
import concurrent.futures
from oceans.params import *
from oceans.utils import timeworker
from oceans.honey_sources import store_to_cloud
from dataclasses import dataclass , field
import functools
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.cloud import storage

#TODO
# import logging

# logging.basicConfig(filename = "logs.txt" ,
#                     format = "%(asctime)s:%(message)s" ,
#                     datefmt = "%Y-%m-%d %H:%M:%S",
#                     level = logging.INFO,
#                     )

@dataclass(slots=True)
class Bee(ABC):

    """Bee Worker Archetype"""

    url : str
    location : str
    drift : float = 30
    headless_bee : bool = True
    height : int = None
    width : int = None
    production_stage : bool = field(default=False,repr=False)
    traveling_timeout : ClassVar[int] = 90
    until_returns_to_hive : ClassVar[int] = 10
    driver : ... = field(init=False,repr=False)
    image : ... = field(init=False,repr=False)
    store_cloud : bool = field(repr = False , default = False)
    MAX_CARGO : ClassVar[int] = 20

    def __post_init__(self) -> None:
        """Please DO NOT modify the Bee Hive code
            without asking for the Bee Queen(Nicole) first!"""

        #configure web driver options
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--mute-audio")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if self.headless_bee:
            options.add_argument('--headless')

        ##initialize webdriver
        self.driver = webdriver.Chrome(options=options)

        if self.height and self.width:
            self.driver.set_window_size(self.width,self.height)

        self.image = None
        print(colored(f"Bee worker 🐝 has been initialized for {self.location}...","blue"))

    @abstractmethod
    def _collect(self) -> None:
        """Fly to honey collection area."""

        ##get page
        self.driver.get(self.url)

    @abstractmethod
    def collect(self) -> ...:
        """Collect honey!"""
        pass

    @staticmethod
    def _validate_production_stage(func : Callable) -> Callable:
        @functools.wraps(func)
        def establish_first_collection(self, *args, **kwargs):
            ##preparing Bee Worker for production stage
            if not self.production_stage:
                then = datetime.now()
                print(colored(f"Bee worker 🐝 is now flying to {self.location}..." , "blue"), flush=True)
                self._collect()
                print(colored(f"""Bee worker 🐝 has arrived at {self.location} after
                                  {(datetime.now() - then).total_seconds():.2f} second(s)
                                  and is ready for collection.""","blue") ,
                                flush = True)

            ##Bee Worker is now on production stage
            return func(self,*args,**kwargs)
        return establish_first_collection

    def switch_flower(self , ifr) -> None:
        self.driver.switch_to.frame(ifr)

    def reset_flower(self) -> None:
        self.driver.switch_to.default_content()

    def store_honey(self , honey_bytes : bytes) -> bool:
        """Bee Worker stores Image to the /images directory."""

        try:
            image_num = self._find_image_number()
            time_now = datetime.now().astimezone(madrid_timezone)
            image_name = f"{type(self).__name__}__ocean__" + time_now.strftime("%Y-%m-%d_%H:%M:%S") + "__" + str(image_num) + ".png"
            path = pathlib.Path( os.path.join( os.path.dirname(__file__) , f"images/{type(self).__name__}"))
            imagepath = path / image_name
            imagepath.parent.mkdir(parents=True, exist_ok=True)
            with imagepath.open(mode="wb") as f_img:
                f_img.write(honey_bytes)
            print(colored(f"Honey from {self.location} was stored succesfully 🍯", "green"),flush=True)
            return True
        except Exception as e:
            print(colored(f"Failed to collect honey from {self.location} ❌", "red"),flush=True)
            print(e)
            return False

    def _find_image_number(self) -> int:
        p = pathlib.Path(os.path.join( os.path.dirname(__file__) , f"images/{type(self).__name__}"))
        p.mkdir(parents=True, exist_ok=True)
        images = [x for x in p.glob("*.png") if x.is_file()]
        return len(images) + 1

    def return_to_hive(self) -> None:
        """Bee stops operating; driver shutdown"""

        print(colored(f"Bee worker 🐝 has finished collection in {self.location}!","blue"),flush=True)
        self.driver.quit()

    @property
    def has_full_cargo(self) -> bool:
        return self.store_cloud and len(os.listdir(os.path.join( os.path.dirname(__file__) , "images", self.location + "Bee"))) > Bee.MAX_CARGO

    def waggle(self , until : float) -> bool:
        """Bee waggles to collect valuable honey"""

        collection_initialized = datetime.now()
        while True:
            ##collect honey
            self.collect()

            if self.image is None:
                self.return_to_hive()
                return False
            elif datetime.now() - collection_initialized > timedelta(minutes=min(until , Bee.until_returns_to_hive)):
                self.return_to_hive()
                return True

            if self.has_full_cargo:
                store_to_cloud(location = self.location)

            image_bytes = self.image.screenshot_as_png
            self.store_honey(image_bytes)
            time.sleep(self.drift)


class ElPortoBee(Bee):

    """El Porto Live Webcam Bee"""

    def _collect(self) -> None:
        #Override
        #call parent
        super()._collect()

        #check if element exists
        ifr = WebDriverWait(self.driver, Bee.traveling_timeout).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@id='gdpr-consent-notice']")))
        self.switch_flower(ifr)
        self.driver.find_element(By.XPATH , "//button[@id='save']").click()
        self.reset_flower()
        self.production_stage = True

    @Bee._validate_production_stage
    def collect(self):
        #Override
        image = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "player-main")))
        self.image = image
        return image


class LaCorunaBee(Bee):

    """La Coruna Live Webcam Bee"""

    def _collect(self) -> None:
        #Override
        #call parent
        #super()._collect()
        #TODO PROBLEM WITH REGISTRATION
        self.production_stage = False
        sys.exit(-1)

    @Bee._validate_production_stage
    def collect(self):
        #Override
        pass


class HawaiBee(Bee):

    """Hawai Live Webcam Bee"""

    def _collect(self) -> None:
        #Override
        #call parent
        super()._collect()

        #check if element exists
        ifr = WebDriverWait(self.driver, Bee.traveling_timeout).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//iframe[@id='widget2']")))

        self.switch_flower(ifr)

        #check if element exists
        _ = WebDriverWait(self.driver, Bee.traveling_timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[starts-with(@class,'ytp-large-play-button')]")))

        #wait until element is clickable
        button = WebDriverWait(self.driver, Bee.traveling_timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH,"//button[starts-with(@class,'ytp-large-play-button')]"))
                ).click()
        self.production_stage = True

    @Bee._validate_production_stage
    def collect(self):
        #Override

        image = self.driver.find_element(By.XPATH, "//video[starts-with(@class,'video-stream')]")
        self.image = image
        return image


class ZarautzBee(Bee):

    """California Live Webcam Bee"""

    def _collect(self) -> None:
        #Override
        #call parent
        super()._collect()

        #check if element exists
        button = WebDriverWait(self.driver, Bee.traveling_timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[starts-with(@class,'ui') and @role='button']")))
        self.driver.execute_script("arguments[0].click();", button)
        self.production_stage = True

    @Bee._validate_production_stage
    def collect(self):
        #Override

        image = self.driver.find_element(By.XPATH, "//div[@class='webcam-iframecontainer']")
        self.image = image
        return image


class NigranBee(Bee):

    """Nigran Live Webcam Bee"""

    def _collect(self) -> None:
        #Override
        #call parent
        super()._collect()

        #check if element exists
        _ = WebDriverWait(self.driver, Bee.traveling_timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[starts-with(@id,'cookie-law')]")))

        #wait until button is clickable
        button = WebDriverWait(self.driver,Bee.traveling_timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH , "//a[@id='cookie_action_close_header']"))
                ).click()

        ifr = self.driver.find_element(By.CSS_SELECTOR, "iframe[sandbox^='allow-forms']")
        self.switch_flower(ifr)
        self.production_stage = True

    @Bee._validate_production_stage
    def collect(self):
        #Override

        image = self.driver.find_element(By.XPATH, "//div[@id='vid']")
        self.image = image
        return image


class Hive:

    """The Great Bee Hive: Use it to instantiate your Bee Workers."""

    def __init__(self) -> None:
        self.video_uris : dict[str,str] = WEBCAM_LOCATIONS
        self.bees : dict[str,Bee] = {
                                    "Nigran": NigranBee,
                                    "ElPorto": ElPortoBee,
                                    "Zarautz" : ZarautzBee,
                                    "Hawai": HawaiBee,
                                    #NOT IMPLEMENTED For LaCoruna due to Registration FireWall
                                    #"LaCoruna":LaCorunaBee
                                    }

    def get_locations(self) -> Iterator[str]:
        return self.bees.keys()

    def get_worker(self , location : str , *args , **kwargs) -> Union[Bee,None]:
        """Returns a Bee Worker given a certain location."""
        location = location.strip()
        WorkerBee = self.bees.get(location)
        if WorkerBee:
            url = self.video_uris.get(location)
            return WorkerBee(url , location , *args, **kwargs)
        else:
            print(colored("Unregisted location: {location}!","red"))
            print("Please use one of the available locations:")
            for location in self.video_uris.keys():
                print(f"{location=}")
            return None

    @staticmethod
    @timeworker
    def create_worker(data : dict[str,Union[str,float,int]]) -> bool:
        until = data.pop("until")
        worker = Hive().get_worker(**data)
        if not worker:
            return False
        return worker.waggle(until)

    @staticmethod
    def initialize_collection(locations : Union[Iterable[str],Iterator[str]] ,
                                headless_bee : bool ,
                                width : int ,
                                store_cloud : bool ,
                                height : int ,
                                drift : float ,
                                until :float) -> None:
        print(f"Total available bee workers in the Hive: {os.cpu_count()}")

        #not allowing duplicate bee locations
        locations = set(locations)

        max_workers = min(os.cpu_count() , len(locations))

        print(f"Please wait while initializing {max_workers} bee workers...")
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            worker_tasks = []
            for location in locations:
                data = dict(location = location , store_cloud = store_cloud , headless_bee = headless_bee , width = width , height = height , drift = drift , until = until)
                worker_tasks.append(executor.submit(Hive.create_worker , data))
                print(f"Creating bee worker for location {location}...")

            concurrent.futures.wait(worker_tasks)
            for task in concurrent.futures.as_completed(worker_tasks):
                status = ("Success ✅","green") if task.result() else ("Failure ❌","red")
                print(f"Job completed status: " + colored(status[0],status[1]))

        print(colored("Honey collection is deemed succesful. ✅", "green"))
        print(colored("All Bee Workers have returned to the Hive. 🛖", "blue"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bee Hive Command Center")
    parser.add_argument("-l","--location", type=str, default="Hawai")
    parser.add_argument("-hb","--headless_bee", type=bool, default=True)
    parser.add_argument("-u","--until", type=int, default=3)
    parser.add_argument("-d","--drift" , type = int , default = 20)
    parser.add_argument("-w","--width", type=int , default=1800)
    parser.add_argument("-ht","--height" , type = int , default = 1000)
    parser.add_argument("-c","--cloud", type = bool , default =  False)
    parser.add_argument("-m","--mode" , type = str , default = "normal", required = True, choices=["normal","multi"])

    print("Initializing honey collection protocol.\nPress Ctrl+C to terminate the collection process...")

    args = parser.parse_args()
    try:
        match args.mode:
            case "normal":
                Hive().get_worker(args.location ,
                                  headless_bee = False,
                                  store_cloud = args.cloud ,
                                  width = args.width ,
                                  height = args.height,
                                  drift = args.drift).waggle(until = args.until)
            case "multi":
                Hive.initialize_collection(locations = Hive().get_locations(),
                                            headless_bee = args.headless_bee,
                                            store_cloud = args.cloud ,
                                            width = args.width,
                                            height = args.height,
                                            drift = args.drift,
                                            until = args.until)
            case _:
                print(colored(f"Unknown mode detected {args.mode}!","red"))
    except KeyboardInterrupt:
        print(colored("All Bees return to the Hive! 🛖", "red"))
    except Exception as e:
        print(f"Wooooops! It seems that the following error occured: {e}")
    finally:
        print(colored("Terminating collection! ❌", "red"))
        sys.exit(1)
