import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM
import KratosMultiphysics.StemApplication as StemKratos

from KratosMultiphysics.StemApplication.set_nodal_parameters_process import SetNodalParametersProcess


def test_add_nodal_parameters_process():


    model = KratosMultiphysics.Model()

    mass_element_model_part = model.CreateModelPart("mass_element_model_part", 1)
    mass_element_model_part.CreateNewNode(1, 0.0, 0.0, 0.0)
    mass_element = mass_element_model_part.CreateNewElement("NodalConcentratedElement2D1N", 1, [1], KratosMultiphysics.Properties(0))

    mass_element_properties = mass_element_model_part.CreateNewProperties(0)

    # available property
    mass_element_properties.SetValue(KratosMultiphysics.NODAL_MASS, 1.0)

    # non-available property
    mass_element_properties.SetValue(KratosMultiphysics.YOUNG_MODULUS, 1.0)

    process = SetNodalParametersProcess(mass_element_model_part,
                                        KratosMultiphysics.Parameters( """{"model_part_name" : "mass_element_model_part"}"""))

    process.ExecuteInitialize()

    # check if nodal mass is now set on element rather than properties
    assert mass_element.GetValue(KratosMultiphysics.NODAL_MASS) == 1.0

    # check if young modulus has not been set
    assert mass_element.GetValue(KratosMultiphysics.YOUNG_MODULUS) == 0.0





if __name__ == '__main__':
    test_add_nodal_parameters_process()
