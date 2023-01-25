"""The Official Editor for Leo's Simulation"""
from Editor_Framework import *
from colors import *
arial20B = makeFont("Arial",20,True)
arial15 = makeFont("Arial",15)
init((900,600)) 
from framework import WIDTH,HEIGHT
window_space = Window_Space()
window_space.addDebugInfo(500) 
def open_settings(): scene.pause_simulation();  window_space.activateMiniWindow('Settings')
def open_presets(): scene.pause_simulation();  window_space.activateMiniWindow('Presets')
window_space.mainSpace = ScrollingMS()
window_space.addMiniWindow('Vector Editor',(WIDTH//2-150,HEIGHT//2-210),(300,425),(120,120,120))
window_space.addMiniWindow('Settings',(WIDTH//2-260,HEIGHT//2-210),(520,425),(120,120,120))
window_space.addMiniWindow('Presets',(WIDTH//2-260,HEIGHT//2-210),(520,425),(120,120,120))
window_space.addBorder('top',35,grey)
window_space.addBorder('bottom',20,dark_grey,2)
window_space.addBorder('right',200,(100,100,100),2)
window_space.addBorder('left',200,(80,80,80))
left_height = window_space.left._size[1]
window_space.bottom.messages = err_box =  TextBox((2,3),makeFont('Arial',14),'',red)
window_space.top.title = TextBox((5,5),arial20B,"Simulation Editor",white)
window_space.mainSpace.scene = scene = Editor_Window((0,0),window_space.MSSize,err_box.setText)
window_space.top.play_button = Button((WIDTH//2-20,5),40,25,scene.toggle_simulation,dark_green,grey,light_green,'Play')
window_space.top.settings_button = Button((180,5),80,25,open_settings,light_dark_grey,grey,dark_light_grey,'Settings',5,2)
window_space.top.presets_button = Button((260,5),80,25,open_presets,light_dark_grey,grey,dark_light_grey,'Presets',5,2)
window_space.left.title = TextBox((0,0),arial20B,"Objects:",white)
window_space.left.object_unselect = Button((5,left_height-35),90,30,scene.UnSelectBody,dark_light_grey,grey,light_grey,arial15.render('Stop Follow',1,black),10,5)
window_space.right.inspector = inspector =  Inspector((0,30),window_space.rightSize)
window_space.right.title = TextBox((0,0),arial20B,"Inspector:",white)
window_space.mainSpace.pause = KeyBoundFunction(scene.toggle_pause_simulation,' ')
window_space.left.zoom_title = TextBox((8,left_height-69),arial15,'Zoom:',light_grey)
window_space.left.zoom_slider = Slider(8,left_height-20-29,90,7,0,1000,lambda x:scene.set_zoom(2**((x-350)/400)),(100,200,100),(50,50,50))
window_space.left.zoom_slider.set_value(350)
window_space.left.hierarchy = hierarchy = Hierarchy((0,25),(window_space.leftSize,HEIGHT-300),err_box.setText)
window_space.left.new_body = Button((5,left_height-99),90,30,scene.set_tool('Place Planet'),dark_light_grey,grey,light_grey,'New Body')
window_space.left.velocities = CheckBox((110,left_height-20),15,scene.set_show_vel,(50,50,50),'Velocity',makeFont('Arial',12),(16,0))
window_space.left.accelerations = CheckBox((110,left_height-50),15,scene.set_show_accel,(50,50,50),'Acceleration',makeFont('Arial',12),(15,0))
window_space.left.tracing = CheckBox((110,left_height-80),15,scene.set_tracing,(50,50,50),'Tracing',makeFont('Arial',12),(15,0))
window_space.miniWindow('Vector Editor').side_panel = side = Side_Panel((0,325),inspector.set_vel)
window_space.miniWindow('Vector Editor').dragger = Vector_Dragger((0,25),(300,300),side.set_vector)
window_space.miniWindow('Settings').settings = Settings_Panel()
window_space.top.pan_button = Button((WIDTH-80*1.1,2),70,30,scene.set_tool('Pan'),light_dark_grey,grey,dark_light_grey,'Pan',20,4)
window_space.top.select_button = Button((WIDTH-80*2.1,2),70,30,scene.set_tool('Select'),light_dark_grey,grey,dark_light_grey,'Select',5,4)
window_space.top.move_button = Button((WIDTH-80*3.1,2),70,30,scene.set_tool('Move'),light_dark_grey,grey,dark_light_grey,'Move',13,4)

def set_object(body:Celestial_Body) -> None:
    inspector.set_object(body)
    window_space.drawBorder('right')
scene.OnSelectBody = set_object
scene.resize(window_space.MSSize)
window_space.first_update()
window_space.first_draw()
while 1:
    myInput = getAllInput()
    if myInput.quitEvent or escape_unicode in myInput.KDQueue:
        window_space.onQuit()
        break
    window_space.update(myInput)
    window_space.draw()