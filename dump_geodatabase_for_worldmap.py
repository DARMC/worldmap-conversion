import arcpy
from arcpy import env
import os
import sys

class EmptyGeodatabaseError(Exception)
    def __init__(self, msg):
        print 'EmptyGeodatabaseError: {}'.format(msg)

def find_all_feature_classes(current_workspace):
    """
    Return a list of all feature classes in current_workplace,
    including those that exist within feature datasets.

    Paramteters
    ----------
    current_workspace : must be a valid geodatabase containing
        at least on feature class

    Returns
    ---------
    paths_to_export : a list of feature classes. If no paths are
        found, (i.e. paths_to_export == []), then the function 
        will not return and an EmptyGeodatabaseError will be
        raised.
    """
    paths_to_export = arcpy.ListFeatureClasses()
    
    # search for additional feature classes in feature datasets
    for fds in arcpy.ListDatasets():
        env.workspace = os.path.join(env.workspace, fds)
        for fc in arcpy.ListFeatureClasses():
            paths_to_export.append(os.path.join(fds, fc))
        env.workspace = current_workspace
    
    if len(paths_to_export) == 0:
        raise EmptyGeodatabaseError
    else:
        return paths_to_export

def ensure_valid_gdb(path):
    """
    Ensures that path points to a file that (1) exists and (2) appears
    to be a filegeodatabase (i.e. a file that has the extension .gdb).
    
    Paramteters
    -----------
    path: a system path identifying a file geodatabase

    Returns
    ----------
    True if the path appears to be a valid geodatabase, otherwise raises
    an IOError with more information for the user
    """
    if not os.path.isfile(path):
        raise IOError("geodatabase path does not appear to point to a file.\n")
    elif path[-4:] != '.gdb':
        raise IOError("path exists, but does not point to a geodatabase.\n")
    else:
        return True

def project_feature_class(infc, folder, projection = 4326):
    """
    Convert a feature class infc from its current projection to a
    new projection, and place the new output in folder. If infc
    does not have a valid spatial reference, then it cannot be
    projected.

    Paramteters
    -----------
    infc : a feature class to be projected

    folder : folder in which output will be placed

    projection : by default, EPSG:4326 (WGS 84), but can be any
        projection WKID.
    """
    dsc = arcpy.Describe(infc)
    shortname = infc.split('\\')[1] if len(infc.split('\\')) == 2 else infc
    if dsc.spatialReference.Name == "Unknown":
        print 'Skipped {} - undefined coordinate system.'.format(shortname)
    else:
        print 'Projecting {}'.format(shortname)
        outfc = os.path.join(folder, shortname + '.shp')
        outcs = arcpy.SpatialReference(projection)
        arcpy.Project_management(infc, outfc, outcs)
        print arcpy.GetMessages()

def dump_geodatabase_to_folder(path, folder='Worldmap Files'):
    """
    Project all feature classes in the geodatabase and save them
    as shapefiles  in a folder
    """
    # make sure that path exists and is a geodatabase
    ensure_valid_gdb(path):

    # set workspace and output folder
    env.workspace = path
    if os.path.isdir(folder):
        os.removedirs(folder)
    os.mkdir(folder)

    # get complete list of FCs to project
    feature_classes = find_all_feature_classes(env.workspace)
    print 'Recovered {0} feature classes to project'.format(len(feature_classes))

    # project feature classes - skipping any with unknown references
    for infc in feature_classes:
        project_feature_class(infc, folder)

if __name__ == '__main__':
    GDB_PATH = 'darmc.gdb'
    dump_geodatabase_to_folder(GDB_PATH)
