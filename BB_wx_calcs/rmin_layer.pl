#!/usr/bin/perl

#computing rising motion inhibition index (rmin) and rewriting out file to add to sounding file
# rmin: mean energy (J/kg) required to lift layer of depth 10 m up 300 m

# also computing temperature deficit for layer starting from surface to height 2200 m

# Constants
$rcp = 287/1004;
$g = 9.8; 
$depth = 10;    # the depth [m] of each layer in the interpolated sounding data
$depth1 = 12; # first layer depth is 12 since ground specified to be at 1288m
$no_lev = 516;   # number of levels

# for rmin
$bot1 = 1288;     # bottom level
$bot = 1300; # first 10 m level
$top = 2200; # "crest" level of interest. 11 levels (100 m) around this
$rtop = 4000; # continue calcs up higher
$no_lay = ($rtop - $bot)/$depth + 1 ; #number of layers including the ground
$ttop = $top - 50;
$top_lev = ($top - $bot)/$depth+1;
$ttop_lev = ($ttop - $bot)/$depth+1;
$lift = 300;     # how high layer lifted
$no_lift = $lift/$depth; #how high lifted in layers
# surface layer will be lifted 302 m...

$infile = $ARGV[0]; # the file containing interpolated sounding data
$outfile = $ARGV[1]; # the output file containing interpolated sounding data

$yr = substr($infile,5,4);
$mn = substr($infile,9,2);
$dy = substr($infile,11,2);
$hr = substr($infile,13,2);
$stn = substr($infile,0,4);

open(OUTFILE,">$outfile");

print "$yr $mn $dy $hr $stn\n";

#Open the file containing the interpolated sounding data,loop through each line and read data into an array

if(open(INFILE, "$infile")) # need to specify directory that real time interpolated soundings will be in
{
  $line = <INFILE>;
  printf OUTFILE ("%s",$line);
  $line = <INFILE>;
  printf OUTFILE ("%s",$line);
  $line = <INFILE>;
  printf OUTFILE ("%s",$line);
  $line = <INFILE>;
  $line = substr($line,0,-1);
  printf OUTFILE ("%s   DEF K RMN JKG\n",$line);
#  $line = <INFILE>;
# now processing the surface layer instead of skipping over
#  $line = substr($line,0,-1);
#  printf OUTFILE ("%s -999.00 -999.00\n",$line);
for ($i=0;$i<=$no_lev-1;$i++) # number of total lines in interpolated sounding file 
 {
  $line = <INFILE>;
  @stuff = split(' +',$line);
    $h[$i] = $stuff[1];
    $p[$i] = $stuff[2];
    $t[$i] = $stuff[3];
    $td[$i] = $stuff[4];
    $rh[$i] = $stuff[5];
    $mx[$i] = $stuff[6];
    $tw[$i] = $stuff[7];
    $tv[$i] = $stuff[8];
    $theta[$i] = $stuff[9];
    $thte[$i] = $stuff[10];
    $thtw[$i] = $stuff[11];
    $s[$i] = $stuff[12];
    $d[$i] = $stuff[13];
    $u[$i] = $stuff[14];
    $v[$i] = $stuff[15];
    $va[$i] = $stuff[16];
    $lp[$i] = $stuff[17];
    $st[$i] = $stuff[18];
    $n[$i] = $stuff[19];
    $ri[$i] = $stuff[20];
    $rmin[$i]= -999;
    $thdef[$i]=-999;
#    print "$i $h[$i] $p[$i]\n";
 }
}


$totb = 0;
$ic = 0;

for ($i=0;$i<=$no_lay;$i++) 
 {
  if ($p[$i] > 0)
  {
  $rmin[$i] = 0;
   $ic++;
  $tk = $t[$i]+273.15;
  $tdk = $td[$i] + 273.15;
# find lcl. compute buoyancy wrt unsat parcel below, sat above
  $tlcl = ( 800 * ($tdk - 56)/(800 + ($tdk - 56 ) * log($tk/$tdk)))+56;
  $plcl = $p[$i] * ($tlcl/$tk)**(1/$rcp); 
#  $tc = $t[$i]+273.15;
# lift parcel
  for ($j=$i+1;$j<=$i+$no_lift;$j++)
   {
   $pj = $p[$j];
   if ($pj>$plcl)
   {
    #unsat
    $tp = $theta[$i] * ($pj/1000)**$rcp;
   }
   else
   {
    #sat
    $tp = WBT($pj,$thte[$i]);
   }
#    $tav = ($tc+tp)/2;
    $b = $g * ($tp - ($t[$j]+273.15))/($t[$j]+273.15);   
#    printf "$i $p[$i] $tc $theta[$i] $thte[$i] $plcl $j $pj $tp $t[$j] $tav $b\n";
    $dep = $depth;
    $dep = $depth1 if ($i < 1); # for surface layer
    $totb = $totb + $b *$dep;
    $rmin[$i] = $rmin[$i] + $b * $dep;
#    $tc = $tp;
   }
  }
 }

#get mean potential temp near top of layer
#Computes the mean temp deficit below crest by taking the diference between tht and th in each 10m layer. 

$thdef = 0;
$jc = 0;

$tht = 0;
$thtc = 0;
for ($i=$ttop_lev;$i<=$ttop_lev+10;$i++) 
 {
  if($p[$i] > 0)
 {
  $tht = $tht + $theta[$i];
  $thtc = $thtc + 1;
 }
 }
$tht = $tht / $thtc;

for ($i=0;$i<=$no_lay-1;$i++) 
 {
  if($p[$i] > 0)
 {
  $thdef[$i] = $theta[$i] - $tht;
 }
 }

for ($i=0;$i<=$no_lay-1;$i++) 
{
   printf OUTFILE ("%7.0f %7.2f %7.2f %7.2f %7.1f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.1f %7.2f %7.2f %7.0f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f\n",$h[$i],$p[$i],$t[$i],$td[$i],$rh[$i],$mx[$i],$tw[$i],$tv[$i],$theta[$i],$thte[$i],$thtw[$i],$s[$i],$d[$i],$u[$i],$v[$i],$va[$i],$lp[$i],$st[$i],$n[$i],$ri[$i],$thdef[$i],$rmin[$i]);
}
 sub WBT {
      #parcel temp if above lcl
      my $pres = $_[0];
      my $tht = $_[1];
      $val = 0;
      $val = $tht - 270. if ($tht>270.);
        $tg = ($tht - .5 * ( $val ) ** 1.05 ) * ( $pres / 1000. ) ** .2;
#*      Set convergence and initial guess in degrees C.
        $epsi = .001;
        $tgnu = $tht - 273.15;
#*      Set a limit of 100 iterations.  Compute TENU, TENUP, the
#C*      THTE's at, one degree above the guess temperature.
#       Do Newton iteration.
        $iter = 0;
        $twb = $t;
        $convrg = 0;
        while ( $iter < 100 and !$convrg ) {
          $iter++;
          $tgnup = $tgnu + 1.;
          $tenu = THTE ( $pres, $tgnu, $tgnu );
          $tenup = THTE ( $pres, $tgnup, $tgnup );
#C*        Compute the correction, DELTG; return on convergence.
          $denom  = $tenup - $tenu;
          if($denom>0)
          {
          $cor  = ( $tht - $tenu ) / ( $tenup - $tenu );
          $tgnu = $tgnu + $cor;
          $convrg = 1 if ( abs($cor) < $epsi );
          }
        }

        if (!$convrg) {
         $wbt = -999;
        }
       
        else {
         $wbt =  $tgnu+273.15;
#	 printf "$pres $tht $tg $tgnu $iter $wbpt\n";
        }
#       print "convrg $convrg wbpt $wbpt\n";

        return $wbt;
 }
#**** SUBROUTINE TO COMPUTE EQUIV POT TEMP
 sub THTE {
   my $p = $_[0];
   my $t = $_[1];
   my $td = $_[2];
   $vapr = 6.112 * exp((17.67 * $td) / ( $td + 243.5 ));
   $corr = (1.001 + (( $p - 100.) / 900.) * .0034);
   $e    = $corr * $vapr;
   $mixr =  .62197 * ($e / ($p - $e)) * 1000.;
# temp of lcl from gempak sub
#   printf " $p $t $td $mixr\n";
  $tlcl = ( 800. * ( $td + 273.15 - 56. ) / ( 800. + ( $td + 273.15 - 56. )* log ( ($t + 273.15) / ($td + 273.15) ) ) ) + 56.;

   $E = (287/1004) * (1. - (.28 * .001 * $mixr) );
   $thtm = (273.15 + $t)*(1000/$p)**$E;
   $e = ((3.376 /$tlcl) - .00254) * ($mixr * (1. + .81*.001*$mixr));
   $thte = $thtm * exp($e);
   return $thte;
 }


#************* SUBROUTINE TO COMPUTE TWBC *******

 sub TWBC {
      my $pres = $_[0];
      my $tmpc = $_[1];
      my $relh = $_[2];
      $A = 6.112;
      $B = 17.67;
      $C = 243.5;
      $EPSI = .622;
      $G = $B * $C;
      $ERRMAX = .001;

      $press = $pres;

        $t = $tmpc;
        $es = 6.11 * (10**((7.5 * $t)/(237.7 + $t)));
        $e = $es * ($relh/100.);
        if ($e != 0 )
        {
          $alogs = .43429*log($e) - .43429*log(6.11);
          $dewc = (237.7 * $alogs)/(7.5 - $alogs);
          $dewc = $t if ( $dewc > $t ) ;
        }
        $tmpk = $t + 273.16;
        $vapr = 6.112 * exp((17.67 * $dewc) / ($dewc + 243.5));
        $corr = (1.001 + (($press - 100) / 900) * .0034);
        $e = $corr * $vapr;
        $rmix = .62197 * ( $e / ($press - $e ));
        $cp = 1005.7 * ( 1. + .887 * $rmix );

        $lvap = (2.500 - .00237 * $t) * 1.0E6;

#       Compute L / cp.

        $rlocp = $lvap / $cp;
                                 #       Do Newton iteration.
        $iter = 0;
        $twb = $t;
        $convrg = 0;
        while ( $iter < 100 and !$convrg ) {
          $iter++;
          $bt = $B * $twb;
          $tpc = $twb + $C;
          $d = ( $press / $A ) * exp( -$bt / $tpc );
          $dm1 = $d - 1.;
          $f = ( $t - $twb ) - $rlocp * ( $EPSI / $dm1 - $rmix );
          $df = - $G  / ( $tpc * $tpc );
          $df = $d * $df * $rlocp * $EPSI / ( $dm1 * $dm1 ) - 1.;
          $cor = $f / $df;
          $twb = $twb - $cor;
          $convrg = 1 if ( abs($cor) < $ERRMAX );
        }

        if (!$convrg) {
         $twbc = -999;
        }
        else {
         $twbc =  $twb;
         $twbc =  $tmpc if ( $twbc > $tmpc );
        }
#       print "convrg $convrg twbf $twbf\n";


        return $twbc;
 }
#************* SUBROUTINE TO COMPUTE WB POT TEMP K *******

 sub WBPT {
      my $pres = $_[0];
      my $tht = $_[1];
      $val = 0;
      $val = $tht - 270. if ($tht>270.);
        $tg = ($tht - .5 * ( $val ) ** 1.05 ) * ( $pres / 1000. ) ** .2;
#*      Set convergence and initial guess in degrees C.
        $epsi = .001;
        $tgnu = $tht - 273.15;
#*      Set a limit of 100 iterations.  Compute TENU, TENUP, the
#C*      THTE's at, one degree above the guess temperature.
#       Do Newton iteration.
        $iter = 0;
        $twb = $t;
        $convrg = 0;
        while ( $iter < 100 and !$convrg ) {
          $iter++;
          $tgnup = $tgnu + 1.;
          $tenu = THTE ( $pres, $tgnu, $tgnu );
          $tenup = THTE ( $pres, $tgnup, $tgnup );
#C*        Compute the correction, DELTG; return on convergence.
          $denom  = $tenup - $tenu;
          if($denom>0)
          {
          $cor  = ( $tht - $tenu ) / ( $tenup - $tenu );
          $tgnu = $tgnu + $cor;
          $convrg = 1 if ( abs($cor) < $epsi );
          }
        }

        if (!$convrg) {
         $wbpt = -999;
        }
        else {
         $wbpt =  $tgnu+273.15;
#	 printf "$pres $tht $tg $tgnu $iter $wbpt\n";
        }
#       print "convrg $convrg wbpt $wbpt\n";

        return $wbpt;
 }


