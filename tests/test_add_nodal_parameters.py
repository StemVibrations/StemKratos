import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM
from KratosMultiphysics.StemApplication.set_nodal_parameters_process import SetNodalParametersProcess


def test_add_nodal_parameters_process_nodal_concentrated_element():
    """
    This test checks if the SetNodalParametersProcess sets the nodal parameters of the model part containing
    a nodal concentrated element. The nodal parameters are set to the values of the properties of the model part.

    """

    # initialize Kratos model
    model = KratosMultiphysics.Model()

    # initialize model part
    mass_element_model_part = model.CreateModelPart("mass_element_model_part", 1)

    # define nodes and elements in model part
    mass_element_model_part.CreateNewNode(1, 0.0, 0.0, 0.0)
    mass_element = mass_element_model_part.CreateNewElement("NodalConcentratedElement2D1N", 1, [1], KratosMultiphysics.Properties(0))

    # initialize properties
    mass_element_properties = mass_element_model_part.CreateNewProperties(0)

    # available property
    mass_element_properties.SetValue(KratosMultiphysics.NODAL_MASS, 1.0)

    # non-available property
    mass_element_properties.SetValue(KratosMultiphysics.YOUNG_MODULUS, 1.0)

    process = SetNodalParametersProcess(mass_element_model_part,
                                        KratosMultiphysics.Parameters(
                                            """{"model_part_name" : "mass_element_model_part"}"""))

    # Execute process
    process.ExecuteInitialize()

    # check if nodal mass is now set on element rather than properties
    assert mass_element.GetValue(KratosMultiphysics.NODAL_MASS) == 1.0

    # check if young modulus has not been set
    assert mass_element.GetValue(KratosMultiphysics.YOUNG_MODULUS) == 0.0


def test_add_nodal_parameters_process_spring_damper_element():
    """
    This test checks if the SetNodalParametersProcess sets the nodal parameters of the model part containing
    a spring damper element. The nodal parameters are set to the values of the properties of the model part.
    """

    # initialize Kratos model
    model = KratosMultiphysics.Model()

    # initialize model part
    spring_damper_element_model_part = model.CreateModelPart("spring_damper_element_model_part", 1)

    # define nodes and elements in model part
    spring_damper_element_model_part.CreateNewNode(1, 0.0, 0.0, 0.0)
    spring_damper_element_model_part.CreateNewNode(2, 0.0, 1.0, 0.0)
    spring_damper_element = spring_damper_element_model_part.CreateNewElement("SpringDamperElement3D", 1, [1, 2],
                                                                              KratosMultiphysics.Properties(0))

    # initialize properties
    spring_damper_element_properties = spring_damper_element_model_part.CreateNewProperties(0)
    spring_damper_element_properties.SetValue(KratosMultiphysics.NODAL_MASS, 1.0)
    spring_damper_element_properties.SetValue(KSM.NODAL_DISPLACEMENT_STIFFNESS, [0, 0, 1.0])
    spring_damper_element_properties.SetValue(KSM.NODAL_ROTATIONAL_STIFFNESS, [0, 1, 1.0])
    spring_damper_element_properties.SetValue(KSM.NODAL_DAMPING_RATIO, [0, 0, 2.0])
    spring_damper_element_properties.SetValue(KSM.NODAL_ROTATIONAL_DAMPING_RATIO, [0, 2, 2.0])

    # non-available property
    spring_damper_element_properties.SetValue(KratosMultiphysics.YOUNG_MODULUS, 1.0)

    # Initialize process
    process = SetNodalParametersProcess(spring_damper_element_model_part,
                                        KratosMultiphysics.Parameters(
                                            """{"model_part_name" : "spring_damper_element_model_part"}"""))

    # Execute process
    process.ExecuteInitialize()

    # check if nodal mass is now set on element rather than properties
    assert spring_damper_element.GetValue(KratosMultiphysics.NODAL_MASS) == 1.0
    assert list(spring_damper_element.GetValue(KSM.NODAL_DISPLACEMENT_STIFFNESS)) == [0, 0, 1.0]
    assert list(spring_damper_element.GetValue(KSM.NODAL_ROTATIONAL_STIFFNESS)) == [0, 1, 1.0]
    assert list(spring_damper_element.GetValue(KSM.NODAL_DAMPING_RATIO)) == [0, 0, 2.0]
    assert list(spring_damper_element.GetValue(KSM.NODAL_ROTATIONAL_DAMPING_RATIO)) == [0, 2, 2.0]

    # check if young modulus has not been set
    assert spring_damper_element.GetValue(KratosMultiphysics.YOUNG_MODULUS) == 0.0
