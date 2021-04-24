#!/bin/bash

mongorestore --host=localhost  --port=25000  --username=root --password=80190221  --authenticationDatabase=admin  ../db --drop
