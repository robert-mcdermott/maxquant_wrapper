#!/usr/bin/python

import os
import sys
import codecs

from optparse import OptionParser
from lxml import etree


class FgczMaxQuant2Scaffold:
    """

    """

    def __init__(self, working_dir=""):
        self.working_dir = working_dir
        pass


    def get_filePaths(self):
        for i in self.maxquant_driver.iterchildren('filePaths'):
            return (map(lambda x: os.path.basename(x.text.replace("\\","/")), i))


    def getFasta(self):
        for i in self.maxquant_driver.iterchildren('fastaFiles'):
            return (map(lambda x: os.path.basename(x.text.replace("\\","/")), i))

    def read_maxquant_driver(self, xml_content=None):
        """

        :param filename:
        :return:
        """

        try:
            self.maxquant_driver = etree.fromstring(xml_content)
        except:
            print "ERROR: parsing maxquant xml driver file failed."
            raise

        print self.get_filePaths()
        print
        print self.getFasta()


        #filePaths = map(lambda x: x.text, self.maxquant_driver.iter('filePaths'))

        #print filePaths
    def compose_scaffold_driver(self, xml_content=None, fasta_dir=None):
        """

        :param xmlcontent:
        :return:
        """


        try:
            file_repo = set(os.listdir(fasta_dir))
        except:
            print "ERROR: failed reading '{0}' ..."
            raise


        scaffold_driver_template = """<Scaffold>
<Experiment name='maxquant_bfabric_app'
    analyzeWithTandem='false'
    connectToNCBI='false'
    condenseDataWhileLoading='true'
    annotateWithGOA='true'
    unimodFile='/misc/FGCZ/SCAFFOLD/parameters/unimod.xml'
    highMassAccuracyScoring='true'>

    <DisplayThresholds name='95%'
        id='thresh'
        proteinProbability='0.95'
        minimumPeptideCount='2'
        peptideProbability='0.95'/>

</Experiment>

</Scaffold>
"""

        parser = etree.XMLParser(remove_blank_text=True)
        try:
            scaffold_driver_xml = etree.fromstring(scaffold_driver_template, parser)
        except:
            print "ERROR: parsing scaffold_driver_template file failed."
            raise


        exp = scaffold_driver_xml.find("Experiment")

        fasta = "{0}".format(self.getFasta()[0])
        if fasta in file_repo:
            print "YEAH - {0}/{1}".format(fasta_dir, fasta)
        else:
            print "ERROR: {0} is not available in {1}".format(fasta, fasta_dir)
            raise

        FastaDatabase = etree.SubElement(exp, "FastaDatabase")
        fastaDatabaseDetails = [('id', fasta), 
            ('path', "{0}/{1}".format(fasta_dir, fasta)),
            ('databaseAccessionRegEx', ">([^ ]*)"),
            ('databaseDescriptionRegEx', ">[^ ]* (.*)"),
            ('decoyProteinRegEx', "REV_|rr\|")]

        map(lambda x: FastaDatabase.set(*x), fastaDatabaseDetails)
        exp.append(FastaDatabase)

        for input_file in self.get_filePaths():
            BiologicalSample = etree.SubElement(exp, "BiologicalSample")
            QuantitativeModel = etree.SubElement(BiologicalSample, "QuantitativeModel")
            QuantitativeSample = etree.SubElement(QuantitativeModel, "QuantitativeSample")

            InputFile = etree.SubElement(BiologicalSample, "InputFile")
            InputFile.text = "{0}".format(self.working_dir)
            inputFileDetails = [('maxQuantExperiment', "{0}".format(os.path.splitext(input_file)[0]))]

            biologicalSampleDetails = [
                    ("database", fasta),
                    ("analyzeAsMudpit", "false"),
                    ("name", os.path.splitext(input_file)[0]),
                    ("description", ""),
                    ("category", os.path.splitext(input_file)[0])]

            quantitativeModelDetails = [('type', "Precursor Intensity")]

            quantitativeSampleDetails = [('category', ''),
                                        ('description', ''),
                                        ('name', os.path.splitext(input_file)[0]),
                                        ('primary', 'false'),
                                        ('reporter', 'Precursor Intensity Sample')]

            map(lambda x: BiologicalSample.set(*x), biologicalSampleDetails)
            map(lambda x: QuantitativeModel.set(*x), quantitativeModelDetails)
            map(lambda x: QuantitativeSample.set(*x), quantitativeSampleDetails)
            map(lambda x: InputFile.set(*x), inputFileDetails)

            exp.append(BiologicalSample)

        Export = etree.SubElement(exp, "Export")
        exportDetails = [('type', 'sf3'), 
            ('thresholds', 'thresh'), 
            ("path", "{0}/scaffold.sf3".format(self.working_dir))]

        map(lambda x: Export.set(*x), exportDetails)
        exp.append(Export)

        return (etree.tostring(scaffold_driver_xml, pretty_print=True))


if __name__ == "__main__":
    """
    """

    parser = OptionParser(usage="usage: %prog -w <workingdirektory> -m <maxquant_dirver.xml> -s <scaffold_driver.xml> -f <fasta_dir>", version="%prog 1.0")

    parser.add_option("-m", "--maxquant_driver_xml",
                      type='string',
                      action="store",
                      dest="maxquant_driver_filename",
                      default="maxquant_driver.xml",
                      help="the location of the maxquant driver file")

    parser.add_option("-s", "--scaffold_driver_xml",
                      type='string',
                      action="store",
                      dest="scaffold_driver_filename",
                      default="scaffold_driver.xml",
                      help="the location of the scaffold driver file")

    parser.add_option("-w", "--working_dir",
                      type='string',
                      action="store",
                      dest="wd",
                      default="/scratch/",
                      help="the location of the working directory")

    parser.add_option("-f", "--fasta_dir",
                      type='string',
                      action="store",
                      dest="fasta_dir",
                      default="/misc/fasta/",
                      help="the location of the FASTA files")




    (options, args) = parser.parse_args()

    print "reading maxquant driver file '{0}' ...".format(options.maxquant_driver_filename)
    with open(options.maxquant_driver_filename, "r") as f:
        maxquant_driver = f.read()

    S2MQ = FgczMaxQuant2Scaffold(working_dir=options.wd)
    S2MQ.read_maxquant_driver(maxquant_driver)
    scaffold_driver = S2MQ.compose_scaffold_driver(fasta_dir=options.fasta_dir)

    print "writting scaffold driver file to '{0}' ...".format(options.scaffold_driver_filename)
    with open(options.scaffold_driver_filename, "w") as f:
        f.write(scaffold_driver)

