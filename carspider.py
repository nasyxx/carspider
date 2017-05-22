#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Life's pathetic, have fun ♡~ Nasy.

Excited without bugs::
    O._.O
    ((=)) +1s

* author: Nasy
* date: May 11, 2017
* email: sy_n@me.com
* file: carspider.py
* license: MIT

Copyright © 2017 by Nasy. All Rights Reserved.
"""
import multiprocessing.dummy as mpd
import tarfile
import time
from typing import List

import bs4
import requests as req

HEADERS = {
    "user-agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 "
        "(KHTML, like Gecko) Version/10.1 Safari/603.1.30"}

BASEURL = "https://www.xin.com"
URL = "/{city}/i{page}/"
CITYS = {"beijing", "shanghai", "chengdu", "suzhou"}
CITYS = {"beijing"}


class CarSpi:
    """A car spider."""

    def __init__(self) -> None:
        """Initaialization."""
        # self.city = city
        # content = bs4.BeautifulSoup(
        #     req.get(
        #         URLSBASE + URLPAGE.format(city=self.city, page=1),
        #         headers=HEADERS).content, "lxml")
        # self.pages = int(content.select(".pageLink li")[-2].text)
        self.urls = set()  # type: Set[str]
        self.details = set()  # type: Set[str]
        # self.citys = set()  # type: Set[str]
        # print("Total Pages \t", self.pages)

    def _gu_callback(self, result: List[str]) -> None:
        """Get urls callback."""
        self.urls |= set(result)
        # for i in result:
        #     try:
        #         self.citys.add(CITYRE.findall(i)[0])
        #     except IndexError:
        #         pass

    def _get_urls(self, page: int, city: str) -> List[str]:
        """Get urls."""
        content = bs4.BeautifulSoup(
            req.get(
                BASEURL + URL.format(city=city, page=page),
                headers=HEADERS,
                timeout=15).content, "lxml")
        urls = [url.attrs.get("href") for url in content.select("a.tit")]
        return urls

    def _gd_callback(self, result: str) -> None:
        """Get detail callback."""
        self.details.add(result)

    def _get_detail(self, url: str) -> str:
        """Get detail."""
        content = bs4.BeautifulSoup(
            req.get(BASEURL + url, headers=HEADERS, timeout=15).content,
            "lxml")
        try:
            res = str(content.select(".cd_m_info_it2")[0]) + str(
                content.select(".cd_m_clxx")[0])
            return res
        except IndexError:
            return ""

    def run(self) -> None:
        """Run this spider."""
        pool = mpd.Pool(4)
        for city in CITYS:
            for page in range(1, 50 + 1):
                pool.apply_async(
                    self._get_urls,
                    args=(page, city),
                    callback=self._gu_callback)
        pool.close()
        pool.join()

        pool = mpd.Pool()
        for url in self.urls:
            pool.apply_async(
                self._get_detail, (url, ), callback=self._gd_callback)
        pool.close()
        pool.join()


SPIPQ = mpd.Queue()
SPIQ = mpd.Queue()


def run() -> None:
    """Run a spider."""
    carspi = CarSpi()
    carspi.run()
    datas = list(carspi.details)
    SPIQ.put(datas)


def w_data() -> int:
    """Write datas."""
    while True:
        try:
            datas = SPIQ.get()
            t = time.strftime("cardata/%Y%m%d")
            with tarfile.open(t + ".tar.gz", "w:gz") as ft:
                with open(t, "w") as f:
                    f.write("|><|".join(datas))
                ft.add(t)
                print("Finished at:\t", time.ctime())
        except KeyboardInterrupt:
            return 1
        except BaseException:
            return 0
    return 0


def close_spi() -> None:
    """Join process."""
    while True:
        try:
            p = SPIPQ.get()
            p.join()
        except BaseException:
            pass


def main() -> None:
    """Yooo main function."""
    mpd.Process(target=w_data).start()
    mpd.Process(target=close_spi).start()
    while True:
        print("Start a new spider at:\t", time.ctime())
        p = mpd.Process(target=run)
        p.start()
        SPIPQ.put(p)
        time.sleep(24 * 3600 * 7)


if __name__ == "__main__":
    main()
