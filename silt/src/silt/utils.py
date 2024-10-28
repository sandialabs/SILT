from .polygon_assists.polygonAssistTest import testAssistGUI,testAssist
# Uncomment after plugins are completed:
#from .polygon_assists.sam_polygonAssist import SegmentAnythingAssistGUI,SegmentAnythingAssistGUI
#from .polygon_assists.activeContours_polygonAssist import ActiveContourAssistGUI,ActiveContour

def get_poly_assist_GUI(method):
    # TODO: This should be made into a more robust function, but this works for now and remains modular 
    # so that interaction can remain the same after update.
    if method == 'Segment Anything Model':
        # Uncomment after plugins are completed:
        #polygonAssistGUI SegmentAnythingAssistGUI 
        pass
    
    elif method == 'Active Contour':
        # Uncomment after plugins are completed:
        #polygonAssistGUI = ActiveContourAssistGUI
        pass
    
    elif method == 'Fake Shift (TEST)':
        polygonAssistGUI = testAssistGUI 
          
    return polygonAssistGUI

def get_poly_assist(method):
    # TODO: This should be made into a more robust function, but this works for now and remains modular 
    # so that interaction can remain the same after update.
    if method == 'Segment Anything Model':
        # Uncomment after plugins are completed:
        #polygonAssist = SAM
        pass
    
    elif method == 'Active Contour':
        print('Loading %s' % method)
        # Uncomment after plugins are completed:
        #polygon_assistant = ActiveContour
        pass
    
    elif method == 'Fake Shift (TEST)':
        print('Loading %s' % method)
        polygon_assistant = testAssist
        
    polygonAssistant = polygon_assistant()       
    return polygonAssistant