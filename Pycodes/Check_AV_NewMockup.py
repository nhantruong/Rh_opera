###check the Offer Location of AnhVu Formwork
import rhinoscriptsyntax as rs
import Rhino

units = 1000

#Location 1
#TamNgoai - Location 1
#point1, X=-3688.4065  Y=-38346.7944  Z=28004.1864
#point2, X=-688.4065  Y=-38346.7944 Z=28273.4273
#point3, X=-688.4065  Y=-41346.7944  Z=28315.1724
#point4, X=-3688.4065  Y=-41346.7944  Z=28059.8923
#TamTrong - Location 1
#point5, X=-3688.4065  Y=-38346.7944  Z=27773.0712
#point6, X=-688.4065  Y=-38346.7944  Z=28071.5637
#point7, X=-688.4065  Y=-41346.7944  Z=28113.2784
#point8, X=-3688.4065  Y=-41346.7944  Z=27846.1030

L1_Pt1 = rs.AddPoint(-3688.4065/units,-38346.7944/units,28004.1864/units)
L1_Pt2 = rs.AddPoint(-688.4065/units,-38346.7944/units,28273.4273/units)
L1_Pt3 = rs.AddPoint(-688.4065/units,-41346.7944/units,28315.1724/units)
L1_Pt4 = rs.AddPoint(-3688.4065/units,-41346.7944/units,28059.8923/units)

L1_Pt5 = rs.AddPoint(-3688.4065/units,-38346.7944/units,27773.0712/units)
L1_Pt6 = rs.AddPoint(-688.4065/units,-38346.7944/units,28071.5637/units)
L1_Pt7 = rs.AddPoint(-688.4065/units,-41346.7944/units,28113.2784/units)
L1_Pt8 = rs.AddPoint(-3688.4065/units,-41346.7944/units,27846.1030/units)

L1_surf1=rs.AddSrfPt([L1_Pt1,L1_Pt2,L1_Pt3,L1_Pt4])
L1_surf2=rs.AddSrfPt([L1_Pt5,L1_Pt6,L1_Pt7,L1_Pt8])

#Location 2
#TamNgoai - Location 2
#1 point, X=50311.5935  Y=-76521.9488  Z=2700.3325
#2 point, X=53311.5935  Y=-75322.1127  Z=2700.3325
#3 point, X=53311.5935  Y=-76703.9410  Z=-299.6695
#4 point, X=50311.5928  Y=-77825.1361  Z=-299.6675
#TamTrong - Location 2
#point, X=50311.5935  Y=-75837.8513  Z=2700.3325
#point, X=53311.5935  Y=-74663.9777  Z=2700.3325
#point, X=53311.5935  Y=-75972.6385  Z=-299.6675
#point, X=50311.5935  Y=-77139.7880  Z=-299.6675

L2_Pt1 = rs.AddPoint([50311.5935/units,-76521.9488/units,2700.3325/units])
L2_Pt2 = rs.AddPoint([53311.5935/units,-75322.1127/units,2700.3325/units])
L2_Pt3 = rs.AddPoint([53311.5935/units,-76703.9410/units,-299.6695/units])
L2_Pt4 = rs.AddPoint([50311.5928/units,-77825.1361/units,-299.6675/units])

L2_Pt5 = rs.AddPoint([50311.5935/units,-75837.8513/units,2700.3325/units])
L2_Pt6 = rs.AddPoint([53311.5935/units,-74663.9777/units,2700.3325/units])
L2_Pt7 = rs.AddPoint([53311.5935/units,-75972.6385/units,-299.6675/units])
L2_Pt8 = rs.AddPoint([50311.5935/units,-77139.7880/units,-299.6675/units])

L2_surf1=rs.AddSrfPt([L2_Pt1,L2_Pt2,L2_Pt3,L2_Pt4])
L2_surf2=rs.AddSrfPt([L2_Pt5,L2_Pt6,L2_Pt7,L2_Pt8])

#Location 3
#TamNgoai - Location 3
#1 point, X=5311.5935 Y=-14346.7944 Z=21288.6674 
#2 point, X=8311.5935  Y=-14346.7944  Z=22065.1659
#3 point, X=8311.5935 Y=-17346.7944 Z=22037.2628
#4 point, X=5311.5935  Y=-17346.7944  Z=21670.6116
#TamTrong - Location 3
#point, X=5311.5935  Y=-14346.7944  Z=20910.3946
#point, X=8311.5935  Y=-14346.7944  Z=21354.8017
#point, X=8311.5935  Y=-17346.7944  Z=20943.6619
#point, X=5311.5935  Y=-17346.7944  Z=21111.8850

L3_Pt1 = rs.AddPoint([5311.5935/units,-14346.7944/units,21288.6674/units])
L3_Pt2 = rs.AddPoint([8311.5935/units,-14346.7944/units,22065.1659/units])
L3_Pt3 = rs.AddPoint([8311.5935/units,-17346.7944/units,22037.2628/units])
L3_Pt4 = rs.AddPoint([5311.5935/units,-17346.7944/units,21670.6116/units])

L3_Pt5 = rs.AddPoint([5311.5935/units,-14346.7944/units,20910.3946/units])
L3_Pt6 = rs.AddPoint([8311.5935/units,-14346.7944/units,21354.8017/units])
L3_Pt7 = rs.AddPoint([8311.5935/units,-17346.7944/units,20943.6619/units])
L3_Pt8 = rs.AddPoint([5311.5935/units,-17346.7944/units,21111.8850/units])

L3_surf1=rs.AddSrfPt([L3_Pt1,L3_Pt2,L3_Pt3,L3_Pt4])
L3_surf2=rs.AddSrfPt([L3_Pt5,L3_Pt6,L3_Pt7,L3_Pt8])