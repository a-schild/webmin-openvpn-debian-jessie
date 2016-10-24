#!/usr/bin/perl

#########################################################################
#   Autori:             Marco Colombo (marco@openit.it)
#                       Giuliano Natali Diaolin (diaolin@openit.it)
#   Copyright:          Open It S.r.l.
#                       Viale Dante, 78
#                       38057 Pergine Valsugana (TN) ITALY
#                       Tel: +39 0461 534800 Fax: +39 0461 538443
##############################################################################

require './openvpn-lib.pl';

# legge parametri da form o da url e li inserisce in hash $in
&ReadParse();

&ReadFieldsCA($in{'ca_name'});

$dir = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$in{'ca_name'}.'/';

$stream = "";

$wadir = POSIX::getcwd();
chdir($dir);

if (-x $config{'zip_cmd'}) { $est = ".zip"; } else { $est = ".tgz"; } 


if ($in{'type_key'} == 2 and -s $dir.$in{'key_name'}.".p12" and -s $dir."dh".$$info_ca{'KEY_SIZE'}.".pem") {
    $namefileout = $in{'key_name'}."-p12".$est;
    $fileout = $dir.$namefileout;
    $list_file = $in{'key_name'}.".p12 dh".$$info_ca{'KEY_SIZE'}.".pem";
    if (-s $dir."ta.key") { $list_file .= " ta.key"; }
    if (-x $config{'zip_cmd'}) {
	$cmd = $config{'zip_cmd'}; 
        $cmd .= " ".$fileout." ".$list_file;
    } else { 
	$cmd = `which tar`;
	chomp($cmd);
	$cmd .= " -cvzf ".$fileout." ".$list_file;
    }
    if (-f $fileout) { unlink($fileout); }

    $failedpk2 = &system_logged($cmd." >/dev/null 2>&1 </dev/null");
    if ($failedpk2) { $failed = $cmd; }
} elsif ($in{'type_key'} == 1 and -s $dir."dh".$$info_ca{'KEY_SIZE'}.".pem" and -s $dir."ca.crt" and -s $dir.$in{'key_name'}.".crt" and -s $dir.$in{'key_name'}.".key") {
    $list_file = $in{'key_name'}.".crt dh".$$info_ca{'KEY_SIZE'}.".pem ".$in{'key_name'}.".key ca.crt";
    $namefileout = $in{'key_name'}.$est;
    $fileout = $dir.$namefileout;
    if (-s $dir."ta.key") { $list_file .= " ta.key"; }
    if (-x $config{'zip_cmd'}) {
	$cmd = $config{'zip_cmd'}; 
        $cmd .= " ".$fileout." ".$list_file;
    } else { 
	$cmd = `which tar`;
	chomp($cmd);
	$cmd .= " -cvzf ".$fileout." ".$list_file;
    }
    if (-f $fileout) { unlink($fileout); }

    $failedkey = &system_logged($cmd." >/dev/null 2>&1 </dev/null");
    if ($failedkey) { $failed .= " ".$cmd; }
}

chdir($wadir);

if ($failed) { &error(&text('zip_fail').$failed); }

open S,$fileout;
while ($row=<S>) { $stream .= $row; }
close S;
unlink($fileout);

print "Content-type: application/octet-stream\n";
print "Content-Disposition: attachment; filename=".$namefileout."\n\n";
print $stream;
