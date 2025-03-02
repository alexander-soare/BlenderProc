import blenderproc as bproc
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('blend_path', nargs='?', default="resources/haven/models/ArmChair_01/ArmChair_01.blend", help="Path to the blend file, from the haven dataset, browse the model folder, for all possible options")
parser.add_argument('haven_path', nargs='?', default="resources/haven", help="The folder where the `hdri` folder can be found, to load an world environment")
parser.add_argument('output_dir', nargs='?', default="examples/datasets/haven/output", help="Path to where the final files will be saved")
args = parser.parse_args()

bproc.init()

# Load the object into the scene
objs = bproc.loader.load_blend(args.blend_path)

# Set a random hdri from the given haven directory as background
haven_hdri_path = bproc.loader.get_random_world_background_hdr_img_path_from_haven(args.haven_path)
bproc.world.set_world_background_hdr_img(haven_hdri_path)

# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([5, -5, 5])
light.set_energy(1000)

# Find point of interest, all cam poses should look towards it
poi = bproc.object.compute_poi(objs)
# Sample five camera poses
for i in range(5):
    # Sample random camera location around the object
    location = bproc.sampler.part_sphere([0, 0, 0], radius=3, part_sphere_dir_vector=[1, 0, 0], mode="SURFACE")
    # Compute rotation based on vector going from location towards poi
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location)
    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)

# activate normal and distance rendering
bproc.renderer.enable_normals_output()
bproc.renderer.enable_distance_output()
# set the amount of samples, which should be used for the color rendering
bproc.renderer.set_samples(350)

# render the whole pipeline
data = bproc.renderer.render()

# write the data to a .hdf5 container
bproc.writer.write_hdf5(args.output_dir, data)
