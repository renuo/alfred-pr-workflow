#!/usr/bin/python
import sys

from workflow import Workflow3


def main(workflow):
    query = workflow.args[0]
    workflow.save_password('ghpr-auth-token', query)
    workflow.send_feedback()


if __name__ == '__main__':
    alfred_workflow = Workflow3()
    sys.exit(alfred_workflow.run(main))
