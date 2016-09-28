import requests
import json
import sys
from .utils import *
import logging

""" This module interacts with the *Images service* running on the *storage* part."""

class ClientImages:

    def __init__(self, images_url="http://127.0.0.1:3000/api/images", host_service="127.0.0.1", port_service=3000, url_path="/api/images/"):
        self.logger = get_logger(__name__, logging.INFO)
        self.session = requests.Session()
        self.url_api = images_url
        self.logger.info("URL images service: "+self.url_api)

    def post_image(self, dict_image):
        """Add an image description"""
        try:
            res = self.session.post(self.url_api, headers={'Content-type': 'application/json'}, json=dict_image)
            if res.status_code == requests.codes.created or res.status_code == requests.codes.ok:
                self.logger.info("POST ["+dict_image['repo_name']+"]  into  "+res.url)
            else:
                self.logger.error(str(res.status_code)+" response: "+res.text)
        except requests.exceptions.ConnectionError as e:
            self.logger.exception("ConnectionError: ")
        except:
            self.logger.exception("Unexpected error:")


    def put_image(self, dict_image):
        """Update an image description"""
        try:
            id_image = self.get_id_image(dict_image['repo_name'])
            res = self.session.put(self.url_api+id_image, headers={'Content-type': 'application/json'}, json=dict_image)
            if res.status_code == requests.codes.ok:
                self.logger.info("UPDATED [" + dict_image['repo_name'] + "] into "+res.url)
            else:
                self.logger.error(str(res.status_code) + " Error code " + res.text)
        except requests.exceptions.ConnectionError as e:
            self.logger.exception("ConnectionError: " )
        except:
            self.logger.exception("Unexpected error:")
            raise
        # else:
        #     return res.json()

    def get_images(self):
        """Get all the images descriptions."""
        try:
            res = self.session.get(self.url_api)
            if res.status_code == requests.codes.ok:
                return res.json()
            else:
                self.logger.error(str(res.status_code) + " Error code. " + res.text)
        except requests.exceptions.ConnectionError as e:
            self.logger.exception("ConnectionError: ")
        except:
            self.logger.exception("Unexpected error:")
            raise

    def get_id_image(self, repo_name):
        """Return the *id* of the *repo_name*."""
        json_image_list = self.get_image(repo_name)
        if json_image_list:
            if "_id" in json_image_list[0].keys():
                return json_image_list[0]['_id']
            else:
                raise Exception(" _id not found in "+repo_name)

    def get_image(self, repo_name):
        """Return the description of a single iamge"""
        url = self.url_api + "?repo_name=" + repo_name
        try:
            res = self.session.get(url)
            return res.json()
        except requests.exceptions.ConnectionError as e:
            self.logger.exception("ConnectionError: ")

    def get_scan_updated(self, repo_name):
        payload = {'repo_name': repo_name, 'select': 'last_scan last_updated'}
        try:
            res = requests.get(self.url_api, params=payload)
            return res.json()
        except requests.exceptions.ConnectionError as e:
            self.logger.exception("ConnectionError: " )

    def is_new(self, repo_name):
        """Check if the image is new into the images service. \n
        An image is new if it is not present."""
        res_json = self.get_image(repo_name)
        if res_json['count'] is 0:
            self.logger.info("["+repo_name+"] is new into IMAGES SERVER")
            return True
        else:
            self.logger.info("[" + repo_name + "] is present")
            return False


    def must_scanned(self, repo_name, tag="latest"):
        """
        Check if the *repo_name* has been scanned recently and it is not require the scan.
         if(local.last_updated > remote.last_scan ) then {scan}
        :param repo_name: the image name.
        :return: True if the image must be scan. False otherwise.
        """

        res_image_json = self.get_scan_updated(repo_name)  # {"images:[
        if res_image_json is not None:   # if not empty list, the result is there
            self.logger.debug("Received from Images service" + str(res_image_json))
            image_json = res_image_json['images'][0]
            self.logger.info("[" + repo_name + "] Images Service last scan: " + str(image_json['last_scan']) + " last update: " + str(image_json[
                'last_updated']))
            dofinder_last_scan = string_to_date(image_json['last_scan'])
            if image_json['last_updated']:
                dofinder_last_update = string_to_date(image_json['last_updated'])
            else:
                dofinder_last_update = dofinder_last_scan   # if is None tha image is not scan again becuse is  equal to last scan

            # latest_updated from docker hub
            url_tag_latest = "https://hub.docker.com/v2/repositories/" + repo_name + "/tags/" + tag
            json_response = self.session.get(url_tag_latest).json()
            hub_last_update_string = json_response['last_updated']
            if(json_response['last_updated']):
                hub_last_update = string_to_date(hub_last_update_string)
            else:
                hub_last_update = dofinder_last_scan

            # if(hub_last_update > dofinder_last__update && hub_last_update > dofinder_last_scan):
            if hub_last_update > dofinder_last_update:
                self.logger.debug("[" + repo_name + "] need to update, last update of docker Hub is greater than last scan")
                return True
            else:
                self.logger.debug("["+repo_name+"] NOT need to scan, last update into docker Hub is less or equal")
                return False

