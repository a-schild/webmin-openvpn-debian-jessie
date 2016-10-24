#!/usr/bin/perl

#########################################################################
#   Autori:             Marco Colombo (marco@openit.it)
#                       Giuliano Natali Diaolin (diaolin@openit.it)
#   Copyright:          Open It S.r.l.
#                       Viale Dante, 78
#                       38057 Pergine Valsugana (TN) ITALY
#                       Tel: +39 0461 534800 Fax: +39 0461 538443
##############################################################################

use File::Copy;

require './openvpn-lib.pl';

# legge parametri da form o da url e li inserisce in hash $in
&ReadParse();

if ($in{'client'}) {
    &ReadVPNConf();

    $in{'ca_dir'} = $config{'openvpn_keys_subdir'}.'/'.$in{'ca'};

    &ReadFieldsCA($in{'ca'});

    File::Copy::copy($config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/ca.crt',$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'); 
    File::Copy::copy($config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/dh'.$$info_ca{'KEY_SIZE'}.'.pem',$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/');
    
    File::Copy::copy($config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/'.$in{'client'}.'.crt',$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'.crt');
    File::Copy::copy($config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/'.$in{'client'}.'.key',$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'.key');

    # crea il file ta.key per la CA, se non esiste
    if ($in{'tls-auth'} == 1) {
	$in{'tls-auth-old'} =~ s/ 0$//;
	File::Copy::copy($config{'openvpn_home'}.'/'.$in{'tls-auth-old'},$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/ta.key');
    }
    
    foreach $mf (qw/up down/) {
	if (-e $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'_'.$mf.'.bat') {
	    unlink($config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'_'.$mf.'.bat');
	}
	if (-s $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'.'.$mf) {
	    open L ,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'.'.$mf;
	    @rows = <L>;
	    close L;
	    open W,'>'.$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'_'.$mf.'.bat';
	    foreach $row (@rows) {
		$row =~ s/\n/\r\n/;
		print W $row;
	    }
	    close W;
	    chmod(0700,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/'.$in{'client'}.'_'.$mf.'.bat');
	}
    }

    $dirin = $in{'client'};
    $dirout = $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'};
} else {
    $dirin = $in{'vpn'};
    $dirout = $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'};
}
$stream = "";

$wadir = POSIX::getcwd();
chdir($dirout);

if (-x $config{'zip_cmd'}) { $est = ".zip"; } else { $est = ".tgz"; } 

$fileout = $dirin.$est;
if (-x $config{'zip_cmd'}) {
    $cmd = $config{'zip_cmd'}." -r ".$fileout." ".$dirin;
} else { 
    $cmd = `which tar`; 
    chomp($cmd); 
    $cmd .= " -cvzf ".$fileout." ".$dirin;
}
if (-f $fileout) { unlink($fileout); }
$failed = &system_logged($cmd." >/dev/null 2>&1 </dev/null");
if ($failed) { $failed = $cmd; }

if ($failed) { &error(&text('zip_fail').$failed); }

open S,$fileout;
while ($row=<S>) { $stream .= $row; }
close S;
unlink($fileout);

chdir($wadir);

print "Content-type: application/octet-stream\n";
print "Content-Disposition: attachment; filename=".$fileout."\n\n";
print $stream;
