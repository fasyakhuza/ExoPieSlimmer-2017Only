from ROOT import TF1

def TheaCorrection(puppipt,  puppieta):
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
