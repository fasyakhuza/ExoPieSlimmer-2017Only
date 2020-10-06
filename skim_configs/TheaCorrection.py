from ROOT import TF1

def TheaCorrection_2016(puppipt,  puppieta):
    puppisd_corrGEN      = TF1("puppisd_corrGEN","[0]+[1]*pow(x*[2],-[3])");
    puppisd_corrGEN.SetParameters(
        1.0062610283313527,
        -1.061605139842829,
        0.07999000770091785,
        1.2045376937033758
        )
    puppisd_corrRECO_cen =  TF1("puppisd_corrRECO_cen","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)");
    puppisd_corrRECO_cen.SetParameters(
        1.0580697294754047,
        -5.919711658680494e-05,
        2.2959995891978987e-07,
        -1.9879547980966887e-10,
        6.673819004293196e-14,
        -7.806042326127009e-18
        )

    puppisd_corrRECO_for = TF1("puppisd_corrRECO_for","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)");
    puppisd_corrRECO_for.SetParameters(
        1.2663842090276962,
        -0.0006584956870371675,
        9.737791509701346e-07,
        -5.93842750830321e-10,
        1.616186706072425e-13,
        -1.6272033815974722e-17)

    genCorr  = 1.
    recoCorr = 1.
    totalWeight = 1.

    genCorr =  puppisd_corrGEN.Eval( puppipt )
    if ( abs(puppieta)  <= 1.3 ) :
        recoCorr = puppisd_corrRECO_cen.Eval( puppipt )
    elif( abs(puppieta) > 1.3 ) :
        recoCorr = puppisd_corrRECO_for.Eval( puppipt )

    totalWeight = genCorr * recoCorr
    return totalWeight



def TheaCorrection_2017(puppipt,  puppieta):
    def puppisd_corrGEN(x):
        return 1+0.0090283*(x**(-2*(0.0099852)))-7.30123*(x**(-1))
    def puppisd_corrRECO_cen(x):
        return (1.04323417805)+(8.20581677106e-05)*x+(-2.23790959145e-08)*(x**2)+(-5.56816212196e-12)*(x**3)+(-2.42702058503e-17)*(x**4)+(5.23731618031e-19)*(x**5)
    def puppisd_corrRECO_for(x):
        return (1.11549406241)+(-2.01425972518e-05)*x+(8.36181961894e-09)*(x**2)+(4.39451437171e-11)*(x**3)+(1.04302756829e-14)*(x**4)+(-2.10404344784e-17)*(x**5)

    genCorr  = 1.
    recoCorr = 1.
    totalWeight = 1.

    genCorr =  puppisd_corrGEN( puppipt )
    if ( abs(puppieta)  <= 1.3 ) :
        recoCorr = puppisd_corrRECO_cen( puppipt )
    elif( abs(puppieta) > 1.3 ) :
        recoCorr = puppisd_corrRECO_for( puppipt )

    totalWeight = genCorr * recoCorr
    return totalWeight


def TheaCorrection_2018(puppipt,  puppieta):
    def puppisd_corrGEN(x):
        return 1+0.0231069*(x**(-2*(0.0704761)))-8.42917*(x**(-1))
    def puppisd_corrRECO_cen(x):
        return (1.06263222851)+(2.97332221436e-05)*x+(-7.31785851974e-09)*(x**2)+(2.53798731754e-13)*(x**3)+(1.68571767997e-16)*(x**4)+(-6.77123709437e-20)*(x**5)
    def puppisd_corrRECO_for(x):
        return (1.11889161475)+(2.68579882197e-05)*x+(-4.30234840782e-09)*(x**2)+(8.27000377942e-12)*(x**3)+(1.45823446695e-15)*(x**4)+(-1.65979484436e-18)*(x**5)

    genCorr  = 1.
    recoCorr = 1.
    totalWeight = 1.

    genCorr =  puppisd_corrGEN( puppipt )
    if ( abs(puppieta)  <= 1.3 ) :
        recoCorr = puppisd_corrRECO_cen( puppipt )
    elif( abs(puppieta) > 1.3 ) :
        recoCorr = puppisd_corrRECO_for( puppipt )

    totalWeight = genCorr * recoCorr
    return totalWeight
