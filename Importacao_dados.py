# Extração dos dados para o banco PostgreSQL

import logging
import sys
import zipfile
from pathlib import Path
import gdown
import pandas as pd
import config
from banco import conectar, executar, inserir_em_lote



