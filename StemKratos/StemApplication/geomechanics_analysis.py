import KratosMultiphysics as Kratos

from KratosMultiphysics.GeoMechanicsApplication.geomechanics_analysis import GeoMechanicsAnalysis
from KratosMultiphysics.StemApplication.geomechanics_solvers_wrapper import CreateSolver


class StemGeoMechanicsAnalysis(GeoMechanicsAnalysis):

    def __init__(self, model, project_parameters):
        super().__init__(model, project_parameters)

    def _CreateSolver(self):
        return CreateSolver(self.model, self.project_parameters)


if __name__ == '__main__':

    parameter_file_name = "ProjectParameters.json"

    with open(parameter_file_name,'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())

    model = Kratos.Model()
    simulation = StemGeoMechanicsAnalysis(model, parameters)
    simulation.Run()
