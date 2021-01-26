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
    # don't export this to the client File::Copy::copy($config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/dh'.$$info_ca{'KEY_SIZE'}.'.pem',$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'vpn'}.'/'.$in{'client'}.'/');

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

if ($in{'format'} =~ /single/) {
    $fileout= $in{'vpn'}.'_'.$in{'client'}.'.ovpn';
    open( my $fh, '>', $fileout) or die "Could not open output file";
    # Append client.ovpn to complete .ovpn file
    my $srcFile= $dirout . '/' . $dirin . '/' . $dirin . '.ovpn';
    open( my $fhi, '<', $srcFile) or die "Could not open input file ".$srcFile;
    while (my $line = <$fhi>) {
        if ($line =~ /ca /)
        {
	    print $fh "<ca>\n";
		$caIn= $dirout . '/' . $dirin . '/ca.crt';
	        open( my $caInFH, '<', $caIn) or die "Could not open input file ".$caIn;
	        while (my $caLine = <$caInFH>) {
	    	    print $fh $caLine;
	        }
	        close $caInFH;
	    print $fh "</ca>\n";
        }
        elsif ($line =~ /cert /)
        {
	    print $fh "<cert>\n";
		$certIn= $dirout . '/' . $dirin . '/'.$dirin.'.crt';
	        open( my $certInFH, '<', $certIn) or die "Could not open input file ".$caIn;
	        while (my $certLine = <$certInFH>) {
	    	    print $fh $certLine;
	        }
	        close $certInFH;
	    print $fh "</cert>\n";
        }
        elsif ($line =~ /^key /)
        {
	    print $fh "<key>\n";
		$keyIn= $dirout . '/' . $dirin . '/'.$dirin.'.key';
	        open( my $keyInFH, '<', $keyIn) or die "Could not open input file ".$keyIn;
	        while (my $keyLine = <$keyInFH>) {
	    	    print $fh $keyLine;
	        }
	        close $keyInFH;
	    print $fh "</key>\n";
        }
        elsif ($line =~ /tls\-auth /)
        {
	    print $fh "<tls-auth>\n";
		$tlsIn= $dirout . '/' . $dirin . '/ta.key';
	        open( my $tlsInFH, '<', $tlsIn) or die "Could not open input file ".$tlsIn;
	        while (my $tlsLine = <$tlsInFH>) {
	    	    print $fh $tlsLine;
	        }
	        close $tlsInFH;
	    print $fh "</tls-auth>\n";
	    print $fh "key-direction 1\n";
	    print $fh "remote-cert-tls server\n";
        }
        else
        {
	    print $fh $line;
	}
    }
    close $fhi;
    close $fh;
}
else
{
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
}
open S,$fileout;
while ($row=<S>) { $stream .= $row; }
close S;
unlink($fileout);

chdir($wadir);

print "Content-type: application/octet-stream\n";
print "Content-Disposition: attachment; filename=".$fileout."\n\n";
print $stream;
