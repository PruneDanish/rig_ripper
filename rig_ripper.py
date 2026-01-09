"""
This script isolates the rig of a selected mesh by validating the selection,
extracting the joint hierarchy influencing the mesh, and deleting all other geometry.
"""

import pymel.all as pymel
import maya.cmds as cmds

selection = pymel.ls(selection = True)

def validate_selection(selection):
    """Validate that the selection contains only mesh faces.

    Args:
        selection (list): The list of selected objects.

    Returns:
        tuple: A tuple containing a boolean indicating validity and a list of valid geometry.
    """

    geometry = []
    for i in selection:
        if pymel.objectType(i) != "mesh":
            pymel.warning("please select only faces")
            return False, geometry
        else:
            geometry.append(i)
    return True, geometry

def get_joint_hierarchy(geometry, root_request = False):
    """Get the joint hierarchy of the influential joints for the given geometry.
    
    Args:
        geometry (list): The list of geometry objects.
        
    Returns:
        list: A list of influential joints and their hierarchy.
    """
    
    # Get the skin cluster from the geometry
    for i in geometry:
        skin_clusters = pymel.ls(pymel.listHistory(i), type='skinCluster')

    # Get all joints influencing the skin clusters
    all_joints = pymel.ls(type='joint')

    influential_joints = []
    
    # Find influential joints for each vertex in the geometry
    for vert in geometry:
        sc = pymel.ls(pymel.listHistory(vert), type = 'skinCluster')[0]
        cluster_influences = pymel.skinCluster(sc, query = True, inf = True)
        
        for j in all_joints:
            if j in cluster_influences:

                weight = pymel.skinPercent(sc, vert, transform = j, query = True)
                
                if weight > 0 and j not in influential_joints:
                    influential_joints.append(j)

    # Start building the joint hierarchy using the influential joints
    joint_hierarchy = []

    # Build the joint hierarchy back to the root
    for j in influential_joints:
        joint_hierarchy.append(j)
        joint_parent = pymel.listRelatives(j, parent=True)

        while joint_parent:
            if joint_parent not in joint_hierarchy:
                joint_hierarchy.append(joint_parent)
            
            joint_parent = pymel.listRelatives(joint_parent, parent=True)
    
    if root_request == False:
        return joint_hierarchy
        
    elif root_request == True:
        for jnt in joint_hierarchy:
            current = pymel.PyNode(j)
            while True:
                parents = pymel.listRelatives(current, parent = True)
                if not parents:
                    root = current
                    break
                current = parents[0]
        return joint_hierarchy, root
    
def isolate_geometry(geometry):
    """Isolate the selected geometry.

    Args:
        geometry (list): The list of geometry objects.
    """
    # Invert selection and delete geometry
    mel.eval("invertSelection;")
    pymel.delete()
    
    # Delete unselected shells
    selection_shells = []
    all_mesh = pymel.ls(type = 'mesh')
    
    all_mesh_transforms = []
    
    for mesh in all_mesh:
        
        mesh_transform = mesh.getParent()
    
        if mesh_transform not in all_mesh_transforms:
            all_mesh_transforms.append(mesh_transform)
    
    for mesh in geometry:
        shape = mesh.node()
        transform = shape.getParent()
        
        
        if transform not in selection_shells:
            selection_shells.append(transform)
    
    shells_for_delete = [mesh for mesh in all_mesh_transforms if mesh not in selection_shells]
    pymel.delete(shells_for_delete)

def isolate_joint_hierarchy(joint_hierarchy):
    """Isolate the joint hierarchy.

    Args:
        joint_hierarchy (list): The list of joints in the hierarchy.
    """
    
    # Select all non-hierarchy joints and delete them
    all_joints = pymel.ls(type='joint')
    pymel.select(all_joints)
    pymel.select(joint_hierarchy, deselect = True)
    mel.eval("doDelete")


def rip_rig(selection):
    """Rip the rig using the selected geometry.

    Args:
        selection (list): The list of selected objects.
    """

    valid, geometry = validate_selection(selection)

    if valid and len(selection) == len(geometry):
        joint_hierarchy = get_joint_hierarchy(geometry)
        isolate_geometry(geometry)
        isolate_joint_hierarchy(joint_hierarchy)


rip_rig(selection)