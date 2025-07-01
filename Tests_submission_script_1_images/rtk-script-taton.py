""" This is a sample script for using RTK (Release the krakens)

It takes a file with a list of manifests to download from IIIF (See manifests.txt) and passes it in a suit of commands:

0. It downloads manifests and transform them into CSV files
1. It downloads images from the manifests
2. It applies YALTAi segmentation with line segmentation
3. It fixes up the image PATH of XML files
4. It processes the text as well through Kraken
5. It removes the image files (from the one hunder object that were meant to be done in group)

The batch file should be lower if you want to keep the space used low, specifically if you use DownloadIIIFManifest.

"""
from rtk.task import KrakenAltoCleanUpCommand, YALTAiCommand, KrakenRecognizerCommand, ExtractZoneAltoCommand
from rtk import utils
import glob
from sys import argv


folders = glob.glob("/home/users/p/philipm/rtk/images/*") #il faut donner le dossier dans lequel se trouve les autres dossiers avec images ou les images seulement

if len(argv) == 2:
    num_workers = int(argv[1])
else:
    num_workers = 5

for i in range(0, len(folders), 4):
    batch = [
        file
        for folder in folders[i:i+4]
        for file in glob.glob(f"{folder}/*")
    ]

    # Apply YALTAi
    print("[Task] Segment")
    yaltai = YALTAiCommand(
        batch,
        binary="/home/users/p/philipm/rtk/yaltaienv/bin/yaltai",
        device="cpu", #il utilise les coeurs de l'ordinateur
        yolo_model="/home/users/p/philipm/rtk/models/seg_megv.pt",
        verbose=True,
        raise_on_error=True,
        allow_failure=False,
        multiprocess=2,  # GPU Memory // 5gb  // sur la VDI, 2 était le maximum possible, sinon l'ordinateur faisait des fautes et sautait des images
        check_content=False
    )
    yaltai.process()

    # Clean-up the relative filepath of Kraken Serialization
    print("[Task] Clean-Up Serialization")
    cleanup = KrakenAltoCleanUpCommand(yaltai.output_files)
    cleanup.process()

    # Apply Kraken
    print("[Task] OCR")
    kraken = KrakenRecognizerCommand(
        yaltai.output_files,
        binary="/home/users/p/philipm/rtk/krakenv/bin/kraken",
        #binary="/home/users/p/philipm/rtk/yaltaienv/bin/kraken",
        device="cpu",
        model="/home/users/p/philipm/rtk/models/fondue_gd_megv_v2.mlmodel",
        multiprocess=2,  # GPU Memory // 3gb  // sur la VDI, 2 était le maximum possible, sinon l'ordinateur faisait des fautes et sautait des images
        check_content=True  # Required ?
    )
    kraken.process()

    print("[Task] Extract")
    task = ExtractZoneAltoCommand(
        kraken.output_files,
        zones=None,
        fmt="tei"
    )
    task.process()
