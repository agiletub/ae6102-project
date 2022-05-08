import numpy as np

from traits.api import HasTraits, Instance
from traits.api import observe, Range, Bool, Enum, Float
from traitsui.api import Item, View, Group
from traitsui.api import CancelButton, HGroup, HSplit


def sphere_data():
    theta, phi = np.mgrid[0:np.pi:180j, 0:2*np.pi:360j]
    r = 25
    x, y = r*np.sin(theta)*np.cos(phi), r*np.sin(theta)*np.sin(phi)
    z = r*np.cos(theta)*np.ones_like(phi)

    return x, y, z


def circle_data():
    theta = np.linspace(0, 2*np.pi, 250)
    r = 25
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    z = np.zeros_like(x)

    return x, y, z


def dihedral_data(no_of_lines):
    n = 2*no_of_lines
    r = 25
    pts_angles = []
    for i in range(n):
        pts_angles.append(i/n*2*np.pi)
    x_e = []
    y_e = []
    x_o = []
    y_o = []
    for i in range(n):
        if i % 2 == 0:
            x_e.append(r*np.cos(pts_angles[i]))
            y_e.append(r*np.sin(pts_angles[i]))
        else:
            x_o.append(r*np.cos(pts_angles[i]))
            y_o.append(r*np.sin(pts_angles[i]))
    return x_e, y_e, x_o, y_o


class Vis(HasTraits):
    from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor
    from mayavi.core.api import PipelineBase
    from mayavi import mlab

    scene = Instance(MlabSceneModel, ())
    plot = Instance(PipelineBase)
    engine = None

    sphere, sphere_source = None, None
    circle, circle_source = None, None
    dim = Enum('3', '2')
    ira = Bool(False)
    refl_arr_type = Enum('Coordinate Arrangement', 'Type A',
                         'Type B', 'Type D')
    view_coxeter_cell = Bool(False)
    plane_1_norm_x, plane_1_norm_y, plane_1_norm_z = (Float(0.),
                                                      Float(1.),
                                                      Float(1.))
    plane_2_norm_x, plane_2_norm_y, plane_2_norm_z = (Float(-1.),
                                                      Float(1.),
                                                      Float(1.))
    plane_3_norm_x, plane_3_norm_y, plane_3_norm_z = (Float(1.),
                                                      Float(-1.),
                                                      Float(1.))
    plane_4_norm_x, plane_4_norm_y, plane_4_norm_z = (Float(1.),
                                                      Float(1.),
                                                      Float(1.))
    line_1, line_2, line_3, line_4 = None, None, None, None
    plane_1, show_plane_1 = None, Bool(False)
    plane_2, show_plane_2 = None, Bool(False)
    plane_3, show_plane_3 = None, Bool(False)
    plane_4, show_plane_4 = None, Bool(False)
    dihedral_arrangement_n = Range(2, 10)
    show_axes = Bool(True)
    dihedral_points_e = None
    dihedral_points_o = None

    x_axis, y_axis, z_axis = None, None, None
    scp_coord_b_1, scp_coord_b_2, scp_coord_b_3 = None, None, None
    scp_abd_1, scp_abd_2, scp_abd_3 = None, None, None
    scp_bd_1, scp_bd_2, scp_bd_3 = None, None, None

    @observe('scene.activated')
    def initalize_plot(self, event=None):
        if self.engine is None:
            engine = self.scene.mlab.get_engine()
            self.engine = engine
            x, y, z = sphere_data()
            self.sphere = self.scene.mlab.mesh(x, y, z)
            x, y, z = circle_data()
            self.circle = self.scene.mlab.plot3d(x, y, z)
            self.sphere_source = self.sphere.parent.parent.parent
            self.circle_source = self.circle.parent.parent.parent
            self.circle.parent.parent.filter.radius = 0.5
            self.sphere.visible = False
            self.circle.visible = False
            # Creation of axes
            t_axis = np.linspace(-30, 30, 100)
            x_axis_x, x_axis_y, x_axis_z = (t_axis,
                                            np.zeros_like(t_axis),
                                            np.zeros_like(t_axis))
            self.x_axis = self.scene.mlab.plot3d(x_axis_x, x_axis_y, x_axis_z)
            y_axis_y, y_axis_x, y_axis_z = (t_axis,
                                            np.zeros_like(t_axis),
                                            np.zeros_like(t_axis))
            self.y_axis = self.scene.mlab.plot3d(y_axis_x, y_axis_y, y_axis_z)
            z_axis_z, z_axis_y, z_axis_x = (t_axis,
                                            np.zeros_like(t_axis),
                                            np.zeros_like(t_axis))
            self.z_axis = self.scene.mlab.plot3d(z_axis_x, z_axis_y, z_axis_z)

            self.x_axis.parent.parent.filter.radius = 0.5
            self.y_axis.parent.parent.filter.radius = 0.5
            self.z_axis.parent.parent.filter.radius = 0.5

            # Creation of Lines
            x = np.linspace(-25, 25, 100)
            y1 = (-(self.plane_1_norm_x/self.plane_1_norm_y))*x
            y2 = (-(self.plane_2_norm_x/self.plane_2_norm_y))*x
            y3 = (-(self.plane_3_norm_x/self.plane_3_norm_y))*x
            y4 = (-(self.plane_4_norm_x/self.plane_4_norm_y))*x
            z = np.zeros_like(x)

            self.line_1 = self.scene.mlab.plot3d(x, y1, z, color=(1, 0, 0))
            self.line_2 = self.scene.mlab.plot3d(x, y2, z, color=(1, 0, 0))
            self.line_3 = self.scene.mlab.plot3d(x, y3, z, color=(1, 0, 0))
            self.line_4 = self.scene.mlab.plot3d(x, y4, z, color=(1, 0, 0))

            self.line_1.parent.parent.filter.radius = 0.7
            self.line_2.parent.parent.filter.radius = 0.7
            self.line_3.parent.parent.filter.radius = 0.7
            self.line_4.parent.parent.filter.radius = 0.7

            self.line_1.visible = False
            self.line_2.visible = False
            self.line_3.visible = False
            self.line_4.visible = False
            # Creation of Planes
            x, y = np.mgrid[-25:25:100j, -25:25:100j]
            z1 = ((-(self.plane_1_norm_x/self.plane_1_norm_z))*x
                  + (-(self.plane_1_norm_y/self.plane_1_norm_z))*y)
            z2 = ((-(self.plane_2_norm_x/self.plane_2_norm_z))*x
                  + (-(self.plane_2_norm_y/self.plane_2_norm_z))*y)
            z3 = ((-(self.plane_3_norm_x/self.plane_3_norm_z))*x
                  + (-(self.plane_3_norm_y/self.plane_3_norm_z))*y)
            z4 = ((-(self.plane_4_norm_x/self.plane_4_norm_z))*x
                  + (-(self.plane_4_norm_y/self.plane_4_norm_z))*y)

            self.plane_1 = self.scene.mlab.mesh(x, y, z1)
            self.plane_2 = self.scene.mlab.mesh(x, y, z2)
            self.plane_3 = self.scene.mlab.mesh(x, y, z3)
            self.plane_4 = self.scene.mlab.mesh(x, y, z4)

            self.plane_1.visible = False
            self.plane_2.visible = False
            self.plane_3.visible = False
            self.plane_4.visible = False

            # Creation of SCPs
            p1 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_coord_b_1 = p1
            p2 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_coord_b_2 = p2
            p3 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_coord_b_3 = p3
            p4 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_abd_1 = p4
            p5 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_abd_2 = p5
            p6 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_abd_3 = p6
            p7 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_bd_1 = p7
            p8 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_bd_2 = p8
            p9 = self.scene.mlab.pipeline.scalar_cut_plane(self.sphere_source)
            self.scp_bd_3 = p9

            self.scp_coord_b_1.visible = False
            self.scp_coord_b_2.visible = False
            self.scp_coord_b_3.visible = False
            self.scp_abd_1.visible = False
            self.scp_abd_2.visible = False
            self.scp_abd_3.visible = False
            self.scp_bd_1.visible = False
            self.scp_bd_2.visible = False
            self.scp_bd_3.visible = False
            origin = np.array([0., 0., 0.])
            self.scp_coord_b_1.implicit_plane.widget.origin = origin
            origin = np.array([0., 0.1, 0.])
            self.scp_coord_b_2.implicit_plane.widget.origin = origin
            origin = np.array([0., 0., 0.])
            self.scp_coord_b_3.implicit_plane.widget.origin = origin
            origin = np.array([0., 0., 0.])
            self.scp_abd_1.implicit_plane.widget.origin = origin
            origin = np.array([0., 0., 0.])
            self.scp_abd_2.implicit_plane.widget.origin = origin
            origin = np.array([0., 0., 0.])
            self.scp_abd_3.implicit_plane.widget.origin = origin
            origin = np.array([0., 0., 0.])
            self.scp_bd_1.implicit_plane.widget.origin = origin
            origin = np.array([0., 0., 0.])
            self.scp_bd_2.implicit_plane.widget.origin = origin
            origin = np.array([0., 0., 0.])
            self.scp_bd_3.implicit_plane.widget.origin = origin

            normal = np.array([1., 0., 0.])
            self.scp_coord_b_1.implicit_plane.widget.normal = normal
            normal = np.array([0., 1., 0.])
            self.scp_coord_b_2.implicit_plane.widget.normal = normal
            normal = np.array([0., 0., 1.])
            self.scp_coord_b_3.implicit_plane.widget.normal = normal
            normal = np.array([1., -1., 0.])
            self.scp_abd_1.implicit_plane.widget.normal = normal
            normal = np.array([0., 1., -1.])
            self.scp_abd_2.implicit_plane.widget.normal = normal
            normal = np.array([-1., 0., 1.])
            self.scp_abd_3.implicit_plane.widget.normal = normal
            normal = np.array([1., 1., 0.])
            self.scp_bd_1.implicit_plane.widget.normal = normal
            normal = np.array([0., 1., 1.])
            self.scp_bd_2.implicit_plane.widget.normal = normal
            normal = np.array([1., 0., 1.])
            self.scp_bd_3.implicit_plane.widget.normal = normal

            self.scp_coord_b_1.implicit_plane.widget.enabled = False
            self.scp_coord_b_2.implicit_plane.widget.enabled = False
            self.scp_coord_b_3.implicit_plane.widget.enabled = False
            self.scp_abd_1.implicit_plane.widget.enabled = False
            self.scp_abd_2.implicit_plane.widget.enabled = False
            self.scp_abd_3.implicit_plane.widget.enabled = False
            self.scp_bd_1.implicit_plane.widget.enabled = False
            self.scp_bd_2.implicit_plane.widget.enabled = False
            self.scp_bd_3.implicit_plane.widget.enabled = False

            x_e, y_e, x_o, y_o = dihedral_data(self.dihedral_arrangement_n)
            z = np.zeros_like(x_e)
            self.dihedral_points_e = self.scene.mlab.points3d(x_e, y_e, z,
                                                              color=(1, 0, 0),
                                                              scale_factor=3.)
            self.dihedral_points_o = self.scene.mlab.points3d(x_o, y_o, z,
                                                              color=(0, 0, 1),
                                                              scale_factor=3.)

            self.dihedral_points_e.visible = False
            self.dihedral_points_o.visible = False
        else:
            pass

    @observe('show_axes,dim')
    def view_axes(self, event=None):
        if self.show_axes and self.dim == '3':
            self.x_axis.visible = True
            self.y_axis.visible = True
            self.z_axis.visible = True
        elif self.show_axes and self.dim == '2':
            self.x_axis.visible = True
            self.y_axis.visible = True
            self.z_axis.visible = False
        else:
            self.x_axis.visible = False
            self.y_axis.visible = False
            self.z_axis.visible = False

    @observe('show_plane_1,plane_1_norm_x,plane_1_norm_y,plane_1_norm_z,dim')
    def edit_plane_1(self, event=None):
        x_t, y_t = np.mgrid[-25:25:100j, -25:25:100j]
        t = np.linspace(-25, 25, 100)
        if self.show_plane_1 and self.dim == '3':
            self.line_1.visible = False
            self.plane_1.visible = True
            if self.plane_1_norm_z == 0:
                if self.plane_1_norm_y == 0:
                    if self.plane_1_norm_x == 0:
                        self.plane_1.visible = False
                    else:
                        self.plane_1.mlab_source.set(x=np.zeros_like(y_t),
                                                     y=x_t, z=y_t)
                    # self.scene.mlab.process_ui_elements()
                else:
                    y_new = (-(self.plane_1_norm_x/self.plane_1_norm_y))*x_t
                    self.plane_1.mlab_source.set(x=x_t, y=y_new, z=y_t)
                    # self.scene.mlab.process_ui_elements()
            else:
                z_new = ((-(self.plane_1_norm_x/self.plane_1_norm_z))*x_t
                         + (-(self.plane_1_norm_y/self.plane_1_norm_z))*y_t)
                self.plane_1.mlab_source.set(z=z_new)
                # self.scene.mlab.process_ui_elements()
        elif self.show_plane_1 and self.dim == '2':
            self.plane_1.visible = False
            self.line_1.visible = True
            if self.plane_1_norm_y == 0:
                self.line_1.mlab_source.set(x=np.zeros_like(t), y=t)
                # self.scene.mlab.process_ui_elements()
            else:
                y_new = (-(self.plane_1_norm_x/self.plane_1_norm_y))*t
                self.line_1.mlab_source.set(y=y_new)
                # self.scene.mlab.process_ui_elements()
        else:
            self.line_1.visible = False
            self.plane_1.visible = False

    @observe('show_plane_2,plane_2_norm_x,plane_2_norm_y,plane_2_norm_z,dim')
    def edit_plane_2(self, event=None):
        x_t, y_t = np.mgrid[-25:25:100j, -25:25:100j]
        t = np.linspace(-25, 25, 100)
        if self.show_plane_2 and self.dim == '3':
            self.line_2.visible = False
            self.plane_2.visible = True
            if self.plane_2_norm_z == 0:
                if self.plane_2_norm_y == 0:
                    if self.plane_2_norm_x == 0:
                        self.plane_2.visible = False
                    else:
                        self.plane_2.mlab_source.set(x=np.zeros_like(y_t),
                                                     y=x_t, z=y_t)
                    # self.scene.mlab.process_ui_elements()
                else:
                    y_new = (-(self.plane_2_norm_x/self.plane_2_norm_y))*x_t
                    self.plane_2.mlab_source.set(x=x_t, y=y_new, z=y_t)
                    # self.scene.mlab.process_ui_elements()
            else:
                z_new = ((-(self.plane_2_norm_x/self.plane_2_norm_z))*x_t
                         + (-(self.plane_2_norm_y/self.plane_2_norm_z))*y_t)
                self.plane_2.mlab_source.set(z=z_new)
                # self.scene.mlab.process_ui_elements()
        elif self.show_plane_2 and self.dim == '2':
            self.plane_2.visible = False
            self.line_2.visible = True
            if self.plane_2_norm_y == 0:
                self.line_2.mlab_source.set(x=np.zeros_like(t), y=t)
                # self.scene.mlab.process_ui_elements()
            else:
                y_new = (-(self.plane_2_norm_x/self.plane_2_norm_y))*t
                self.line_2.mlab_source.set(y=y_new)
                # self.scene.mlab.process_ui_elements()
        else:
            self.line_2.visible = False
            self.plane_2.visible = False

    @observe('show_plane_3,plane_3_norm_x,plane_3_norm_y,plane_3_norm_z,dim')
    def edit_plane_3(self, event=None):
        x_t, y_t = np.mgrid[-25:25:100j, -25:25:100j]
        t = np.linspace(-25, 25, 100)
        if self.show_plane_3 and self.dim == '3':
            self.line_3.visible = False
            self.plane_3.visible = True
            if self.plane_3_norm_z == 0:
                if self.plane_3_norm_y == 0:
                    if self.plane_3_norm_x == 0:
                        self.plane_3.visible = False
                    else:
                        self.plane_3.mlab_source.set(x=np.zeros_like(y_t),
                                                     y=x_t, z=y_t)
                    # self.scene.mlab.process_ui_elements()
                else:
                    y_new = (-(self.plane_3_norm_x/self.plane_3_norm_y))*x_t
                    self.plane_3.mlab_source.set(x=x_t, y=y_new, z=y_t)
                    # self.scene.mlab.process_ui_elements()
            else:
                z_new = ((-(self.plane_3_norm_x/self.plane_3_norm_z))*x_t
                         + (-(self.plane_3_norm_y/self.plane_3_norm_z))*y_t)
                self.plane_3.mlab_source.set(z=z_new)
                # self.scene.mlab.process_ui_elements()
        elif self.show_plane_3 and self.dim == '2':
            self.plane_3.visible = False
            self.line_3.visible = True
            if self.plane_3_norm_y == 0:
                self.line_3.mlab_source.set(x=np.zeros_like(t), y=t)
                # self.scene.mlab.process_ui_elements()
            else:
                y_new = (-(self.plane_3_norm_x/self.plane_3_norm_y))*t
                self.line_3.mlab_source.set(y=y_new)
                # self.scene.mlab.process_ui_elements()
        else:
            self.line_3.visible = False
            self.plane_3.visible = False

    @observe('show_plane_4,plane_4_norm_x,plane_4_norm_y,plane_4_norm_z,dim')
    def edit_plane_4(self, event=None):
        x_t, y_t = np.mgrid[-25:25:100j, -25:25:100j]
        t = np.linspace(-25, 25, 100)
        if self.show_plane_4 and self.dim == '3':
            self.line_4.visible = False
            self.plane_4.visible = True
            if self.plane_4_norm_z == 0:
                if self.plane_4_norm_y == 0:
                    if self.plane_4_norm_x == 0:
                        self.plane_4.visible = False
                    else:
                        self.plane_4.mlab_source.set(x=np.zeros_like(y_t),
                                                     y=x_t,
                                                     z=y_t)
                    # self.scene.mlab.process_ui_elements()
                else:
                    y_new = (-(self.plane_4_norm_x/self.plane_4_norm_y))*x_t
                    self.plane_4.mlab_source.set(x=x_t, y=y_new, z=y_t)
                    # self.scene.mlab.process_ui_elements()
            else:
                z_new = ((-(self.plane_4_norm_x/self.plane_4_norm_z))*x_t
                         + (-(self.plane_4_norm_y/self.plane_4_norm_z))*y_t)
                self.plane_4.mlab_source.set(z=z_new)
                # self.scene.mlab.process_ui_elements()
        elif self.show_plane_4 and self.dim == '2':
            self.plane_4.visible = False
            self.line_4.visible = True
            if self.plane_4_norm_y == 0:
                self.line_4.mlab_source.set(x=np.zeros_like(t), y=t)
                # self.scene.mlab.process_ui_elements()
            else:
                y_new = (-(self.plane_4_norm_x/self.plane_4_norm_y))*t
                self.line_4.mlab_source.set(y=y_new)
                # self.scene.mlab.process_ui_elements()
        else:
            self.line_4.visible = False
            self.plane_4.visible = False

    @observe('ira,refl_arr_type,dim')
    def refl_arr(self, event=None):
        self.scp_coord_b_1.implicit_plane.widget.enabled = False
        self.scp_coord_b_2.implicit_plane.widget.enabled = False
        self.scp_coord_b_3.implicit_plane.widget.enabled = False
        self.scp_abd_1.implicit_plane.widget.enabled = False
        self.scp_abd_2.implicit_plane.widget.enabled = False
        self.scp_abd_3.implicit_plane.widget.enabled = False
        self.scp_bd_1.implicit_plane.widget.enabled = False
        self.scp_bd_2.implicit_plane.widget.enabled = False
        self.scp_bd_3.implicit_plane.widget.enabled = False
        cond_temp = self.refl_arr_type == 'Coordinate Arrangement'
        cond_1 = cond_temp and self.dim == '3'
        cond_2 = self.refl_arr_type == 'Type A' and self.dim == '3'

        if self.ira:
            self.show_plane_1 = False
            self.show_plane_2 = False
            self.show_plane_3 = False
            self.show_plane_4 = False
            self.show_axes = False
        if (self.ira and cond_1):
            self.scp_coord_b_1.visible = True
            self.scp_coord_b_2.visible = True
            self.scp_coord_b_3.visible = True
            self.scp_abd_1.visible = False
            self.scp_abd_2.visible = False
            self.scp_abd_3.visible = False
            self.scp_bd_1.visible = False
            self.scp_bd_2.visible = False
            self.scp_bd_3.visible = False
            self.circle.visible = False
        elif (self.ira and cond_2):
            self.scp_coord_b_1.visible = False
            self.scp_coord_b_2.visible = False
            self.scp_coord_b_3.visible = False
            self.scp_abd_1.visible = True
            self.scp_abd_2.visible = True
            self.scp_abd_3.visible = True
            self.scp_bd_1.visible = False
            self.scp_bd_2.visible = False
            self.scp_bd_3.visible = False
            self.circle.visible = False
        elif self.ira and self.refl_arr_type == 'Type B' and self.dim == '3':
            self.scp_coord_b_1.visible = True
            self.scp_coord_b_2.visible = True
            self.scp_coord_b_3.visible = True
            self.scp_abd_1.visible = True
            self.scp_abd_2.visible = True
            self.scp_abd_3.visible = True
            self.scp_bd_1.visible = True
            self.scp_bd_2.visible = True
            self.scp_bd_3.visible = True
            self.circle.visible = False
        elif self.ira and self.refl_arr_type == 'Type D' and self.dim == '3':
            self.scp_coord_b_1.visible = False
            self.scp_coord_b_2.visible = False
            self.scp_coord_b_3.visible = False
            self.scp_abd_1.visible = True
            self.scp_abd_2.visible = True
            self.scp_abd_3.visible = True
            self.scp_bd_1.visible = True
            self.scp_bd_2.visible = True
            self.scp_bd_3.visible = True
            self.circle.visible = False
        elif self.ira and self.dim == '2':
            self.scp_coord_b_1.visible = False
            self.scp_coord_b_2.visible = False
            self.scp_coord_b_3.visible = False
            self.scp_abd_1.visible = False
            self.scp_abd_2.visible = False
            self.scp_abd_3.visible = False
            self.scp_bd_1.visible = False
            self.scp_bd_2.visible = False
            self.scp_bd_3.visible = False
            self.circle.visible = True
        else:
            self.scp_coord_b_1.visible = False
            self.scp_coord_b_2.visible = False
            self.scp_coord_b_3.visible = False
            self.scp_abd_1.visible = False
            self.scp_abd_2.visible = False
            self.scp_abd_3.visible = False
            self.scp_bd_1.visible = False
            self.scp_bd_2.visible = False
            self.scp_bd_3.visible = False
            self.circle.visible = False

    @observe('dim,ira,dihedral_arrangement_n')
    def dihedral_arr(self, event=None):
        if self.dim == '2' and self.ira:
            x_e, y_e, x_o, y_o = dihedral_data(self.dihedral_arrangement_n)
            z = np.zeros_like(x_e)
            self.dihedral_points_e.mlab_source.reset(x=x_e, y=y_e, z=z)
            self.dihedral_points_o.mlab_source.reset(x=x_o, y=y_o, z=z)
            self.dihedral_points_e.visible = True
            self.dihedral_points_o.visible = True
        else:
            self.dihedral_points_e.visible = False
            self.dihedral_points_o.visible = False
    # The layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=500, show_label=False),
                HSplit(
                Group(
                        Item(name='show_axes', label='Show Axes'),
                        Item(name='dim', label='Ambient Space Dim.'),
                        label='General',
                        show_border=True
                     ),
                Group(
                        Item(name='ira',
                             label='Reflection Arrangement Mode'),
                        Item(name='dihedral_arrangement_n',
                             enabled_when='ira is True and dim=="2"',
                             label='No. of Lines in Dihedral Arr.'),
                        Item(name='refl_arr_type',
                             enabled_when='ira is True and dim=="3"',
                             label='Arrangement Type'),
                        label='Reflection Arrangements',
                        show_border=True
                     )),
                HGroup(
                        Item(name='plane_1_norm_x', label='x'),
                        Item(name='plane_1_norm_y', label='y'),
                        Item(name='plane_1_norm_z', label='z',
                             enabled_when='dim == "3"'),
                        Item(name='show_plane_1', label='Show'),
                        label='Hyperplane 1 (Normal)',
                        show_border=True,
                        enabled_when='ira is False'
                        ),
                HGroup(
                        Item(name='plane_2_norm_x', label='x'),
                        Item(name='plane_2_norm_y', label='y'),
                        Item(name='plane_2_norm_z', label='z',
                             enabled_when='dim == "3"'),
                        Item(name='show_plane_2', label='Show'),
                        label='Hyperplane 2 (Normal)',
                        show_border=True,
                        enabled_when='ira is False'
                        ),
                HGroup(
                        Item(name='plane_3_norm_x', label='x'),
                        Item(name='plane_3_norm_y', label='y'),
                        Item(name='plane_3_norm_z', label='z',
                             enabled_when='dim == "3"'),
                        Item(name='show_plane_3', label='Show'),
                        label='Hyperplane 3 (Normal)',
                        show_border=True,
                        enabled_when='ira is False'
                        ),
                HGroup(
                        Item(name='plane_4_norm_x', label='x'),
                        Item(name='plane_4_norm_y', label='y'),
                        Item(name='plane_4_norm_z', label='z',
                             enabled_when='dim == "3"'),
                        Item(name='show_plane_4', label='Show'),
                        label='Hyperplane 4 (Normal)',
                        show_border=True,
                        enabled_when='ira is False'
                        ),
                resizable=True,
                buttons=[CancelButton]
                )


if __name__ == '__main__':
    Vis().configure_traits()
