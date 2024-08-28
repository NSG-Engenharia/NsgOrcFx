from dataclasses import dataclass
import OrcFxAPI as _ofx


# ==== SNCurve CLASS ==== #
@dataclass
class SNCurve:
    """
    S-N (stress range versus cycles) curve according to the equation
    log(N) = log(a) - m.log(S)
    Obs.: pressure unit in MPa
    """
    name: str               # name of the S-N curve
    environment: str          # air or seawater
    m1: float               # m for the low cycle region (N < N_boundary)
    log_a1: float           # log(a) for the low cycle region (N < N_boundary)
    N_boundary: int = None         # number of cycles between the low and high cycle regions
    m2: float = None        # m for the hogh cycle region (N > N_boundary)
    log_a2: float = None    # log(a) for the hogh cycle region (N > N_boundary)

    def setToAnalysis(
            self,
            analysis: _ofx.FatigueAnalysis,
            snCurveIndex: int = 0
            ) -> None:
        """
        Set the current curve to the Fatigue Analysis (S-N curves page)
        * analysis: FatigueAnalysis object
        * tableLineNumber: line of the table of S-N curves page where the curve will be defined
        """
        if analysis.SNcurveCount < snCurveIndex+1: analysis.SNcurveCount = snCurveIndex+1
        analysis.SelectedSNcurveIndex = snCurveIndex
        analysis.SNcurveName[snCurveIndex] = self.name + ' ' + self.environment
        analysis.SNcurveSpecificationMethod = 'Parameters'
        analysis.SNcurvem1 = self.m1
        analysis.SNcurveloga1 = self.log_a1 + 3*self.m1 # pressure in kPa

        if self.m2 != None:
            analysis.SNcurveRegionBoundary = self.N_boundary
            analysis.SNcurvem2 = self.m2
        else:
            analysis.SNcurveRegionBoundary = _ofx.OrcinaInfinity()

        analysis.SNcurveMeanStressModel = 'None'


# ==== Curves ==== #
F3s = SNCurve('F3', 'seawater', 3.0, 11.146, 1e6, 5.0, 14.576)


# ==== Selection function ==== #
def selectSNCurveByName(name: str, environment: str) -> SNCurve:
    """Name (e.g, 'F1') and environment ('air' or 'seawater')"""
    if name == 'F3' and environment == 'seawater': return F3s
    else:
        raise Exception(f'Curve {name} in {environment} not available.')
