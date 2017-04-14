#!/usr/bin/env python

import argparse
import cfg


arguments = argparse.ArgumentParser()
arguments.add_argument("-c", "--config", help="set the configfile",
                       default="config.yaml")


if __name__ == "__main__":
    args = arguments.parse_args()
    cfg.load_config(args.config)

    from webapp import app
    app.debug = True
    app.run()
