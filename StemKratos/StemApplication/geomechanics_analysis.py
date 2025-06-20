import KratosMultiphysics as Kratos
import KratosMultiphysics.GeoMechanicsApplication as KratosGeo

from KratosMultiphysics.analysis_stage import AnalysisStage
from KratosMultiphysics.GeoMechanicsApplication.geomechanics_analysis import GeoMechanicsAnalysis
from KratosMultiphysics.StemApplication.geomechanics_solvers_wrapper import CreateSolver


class StemGeoMechanicsAnalysis(GeoMechanicsAnalysis):
    """
    This class is a specialized version of the GeoMechanicsAnalysis class for the STEM application.

    Inheritance:
        - :class:`KratosMultiphysics.GeoMechanicsApplication.geomechanics_analysis.GeoMechanicsAnalysis`
    """

    def __init__(self, model: Kratos.Model, project_parameters: Kratos.Parameters):
        """
        Constructor for the StemGeoMechanicsAnalysis class.

        Args:
            model (Kratos.Model): The Kratos model containing the model parts.
            project_parameters (Kratos.Parameters): The project parameters for the analysis.
        """
        super().__init__(model, project_parameters)

    def Initialize(self):
        """
        Initialize stage. This runs initialize AnalysisStage instead of GeoMechanicsAnalysis.Initialize. Such that
        displacements are not set to 0.
        """

        # Run initalize AnalysisStage instead of GeoMechanicsAnalysis.Initialize
        AnalysisStage.Initialize(self)

        # In GeoMechanicsAnalysis, DISPLACEMENT and ROTATION will be set to zero every stage. This prevents
        # this behavior in the STEM application. Instead the constitutive law will be reset at the end of each stage.
        self._GetSolver().main_model_part.ProcessInfo[KratosGeo.RESET_DISPLACEMENTS] = self.reset_displacements
        if self.reset_displacements:
            self.ResetIfHasNodalSolutionStepVariable(KratosGeo.TOTAL_DISPLACEMENT)
            Kratos.VariableUtils().UpdateCurrentToInitialConfiguration(
                self._GetSolver().GetComputingModelPart().Nodes)

    def Finalize(self):
        """
        Finalize stage and reset constitutive law of each element
        """
        super().Finalize()

        for element in self._GetSolver().GetComputingModelPart().Elements:
            element.ResetConstitutiveLaw()

        # todo this methodology works for linear elastic, but maybe not for non linear materials in multistage analysis
        # but if this is not done, uvec will not work in multistage analysis. Kratos issue: #13546


    def _CreateSolver(self):
        return CreateSolver(self.model, self.project_parameters)


if __name__ == '__main__':

    parameter_file_name = "ProjectParameters.json"

    with open(parameter_file_name,'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())

    model = Kratos.Model()
    simulation = StemGeoMechanicsAnalysis(model, parameters)
    simulation.Run()
