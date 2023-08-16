__author__ = "NSG Engenharia"
__copyright__ = "Copyright 2023"
__credits__ = ["Gabriel Nascimento"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Gabriel Nascimento"
__email__ = "gabriel.nascimento@nsgeng.com"
__status__ = "Development"


"""
# Library of complementary tools for the OrcaFlex API (OrcFxAPI)
#
#
#
"""

import OrcFxAPI as orc


class Model(orc.Model):
    def getAllLines(self) -> list[orc.OrcaFlexLineObject]:
        """Returns a list of all line objects"""
        lineList = []
        for obj in self.objects:
            if obj.type == orc.ObjectType.Line:
                lineList.append(obj)
        return lineList
