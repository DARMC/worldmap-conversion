import arcpy
from arcpy import env
import os
import sys

GDB_PATH = r'C:\Users\bmd\Desktop\darmc_beta_version\darmc.gdb'

def find_all_fcs(current_workspace):
    """
    Return a list of all feature classes in current_workspace
    """
    paths_to_export = arcpy.ListFeatureClasses()
    
    # search for additional feature classes in feature datasets
    for fds in arcpy.ListDatasets():
        env.workspace = os.path.join(env.workspace, fds)
        for fc in arcpy.ListFeatureClasses():
            paths_to_export.append(os.path.join(fds, fc))
        env.workspace = current_workspace
    
    # warn user if no paths are found
    if len(paths_to_export) == 0:
        print '> WARNING: No feature classes were found in this workspace'

    return paths_to_export

def is_valid_gdb(path):
    """
    Return True if path points to a valid geodatabase
    """
    if not os.path.exists(path):
        print '> ERROR: path does not appear to point to a file'
        return False
    elif path[-4:] != '.gdb':
        print path[-4:]
        print '> ERROR: path exists, but does not point to a geodatabase'
        return False
    else:
        return True

def dump_geodatabase_to_folder(path, projection=4326, folder='Worldmap Files'):
    """
    Project all feature classes in the geodatabase and save them
    as shapefiles  in a folder
    """

    # make sure that path exists and is a geodatabase
    if not is_valid_gdb(path):
        sys.exit()

    # set workspace
    env.workspace = path

    # set up an empty folder to write re-projected data files
    if os.path.isdir(folder):
        os.removedirs(folder)
    os.mkdir(folder)

    # get complete list of FCs to project
    feature_classes = find_all_fcs(env.workspace)
    print 'Recovered {0} feature classes to project'.format(len(feature_classes))

    # project feature classes - skipping any with unknown references
    for infc in feature_classes[0:5]:
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

if __name__ == '__main__':
    dump_geodatabase_to_folder(GDB_PATH)

