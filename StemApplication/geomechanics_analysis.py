import KratosMultiphysics as Kratos

from KratosMultiphysics.GeoMechanicsApplication.geomechanics_analysis import GeoMechanicsAnalysis
import KratosMultiphysics.StemApplication.geomechanics_solvers_wrapper


class StemGeoMechanicsAnalysis(GeoMechanicsAnalysis):

    def __init__(self, model, project_parameters):
        super().__init__(model, project_parameters)

    def _CreateSolver(self):
        return stem_geomechanics_solvers_wrapper.CreateSolver(self.model, self.project_parameters)

if __name__ == '__main__':
    from sys import argv

    if len(argv) > 2:
        err_msg =  'Too many input arguments!\n'
        err_msg += 'Use this script in the following way:\n'
        err_msg += '- With default parameter file (assumed to be called "ProjectParameters.json"):\n'
        err_msg += '    "python geomechanics_analysis.py"\n'
        err_msg += '- With custom parameter file:\n'
        err_msg += '    "python geomechanics_analysis.py <my-parameter-file>.json"\n'
        raise Exception(err_msg)

    if len(argv) == 2: # ProjectParameters is being passed from outside
        parameter_file_name = argv[1]
    else: # using default name
        parameter_file_name = "ProjectParameters.json"

    with open(parameter_file_name,'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())

    model = Kratos.Model()
    simulation = StemGeoMechanicsAnalysis(model, parameters)
    simulation.Run()
