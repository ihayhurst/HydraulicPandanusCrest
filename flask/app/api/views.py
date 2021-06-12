from flask import Blueprint
from werkzeug.utils import redirect
from flask_restful import Api, Resource, reqparse, url_for, abort
import datetime
import markdown
import os
from time import sleep
import pandas as pd
from ..HPCapps import tasks

api_pages = Blueprint("api_pages", __name__)
api = Api(api_pages)


def dump_date(thing):
    if isinstance(thing, datetime.datetime):
        return thing.isoformat()
    return thing


@api_pages.route("/")
def api_home():
    """Present some documentation"""

    # Open the README file
    with open(os.path.join(api_pages.root_path) + "/README.md", "r") as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        md = markdown.markdown(content, extensions=["tables", "fenced_code", "toc"])
        return md


class Inventory(Resource):
    def get(self):
        job = tasks.getQueuedInventoryJSON.delay()
        sleep(1)
        print(url_for('api_pages.taskstatus', jobid=job.id))
        #return 'accepted', 202, {'Location': url_for('api_pages.taskstatus', jobid=job.id)}
        return redirect(url_for('api_pages.taskstatus', jobid=job.id))


class GetTaskStatus(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("jobid", type=str, location="args")
        super(GetTaskStatus, self).__init__()

    def get(self, jobid=None):
        """
        Return status about an asynchronous task. If this request returns a 202
        status code, it means that task hasn't finished yet. Else, the response
        from the task is returned.
        """
        args = self.reqparse.parse_args()
        if args["jobid"] is not None:
            jobid = args["jobid"]

        task = tasks.get_job(jobid)
        if task is None:
            abort(404)
        if task.state  !="SUCCESS":
            # return '', 202, {'Location': url_for('api_pages.GetTaskStatus', jobid=jobid)}
            return redirect(url_for('api_pages.taskstatus', jobid=jobid))
        return task.result, 201


# Resources
# Inventory
api.add_resource(Inventory, "/inventory", endpoint="inventory")
api.add_resource(GetTaskStatus, '/status/<jobid>', endpoint='taskstatus')
