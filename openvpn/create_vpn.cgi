#!/usr/bin/perl -w

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

$error = "";

# Controlli parametri form
if (!-d $config{'openvpn_home'}.'/'.$in{'ca_dir'} or !-s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/ca.key' or !-s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/ca.crt' or !-s $config{'openvpn_home'}.'/'.$in{'dh'}) {
    $error .= $text{'error_not_ca'}.'<BR>';
}

if (($in{'VPN_NAME'} !~ /^[a-zA-Z0-9_\-\.]{4,}$/) or ($in{'VPN_NAME'} =~ /\.{2,}/) or ($in{'VPN_NAME'} =~ /\.$/)){
    $error .= $text{'error_vpn_notok'}.' $&<BR>';
} elsif (-s $config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.'.conf' and $in{'modify'} != 1) {
    $error .= $text{'error_vpn_exist'}.'<BR>';
}

if ($in{'port'} =~ /\D/) {
    $error .= $text{'error_port'}.'<BR>';
}

if (($in{'devbr'} !~ /^\w{2,3}\d/) && ($in{'dev'} =~ /^tap/)){
    $error .= $text{'error_bridge_device'}.'<BR>';
}

if (($in{'netdevbr'} !~ /^\w\w\w\d+/) && ($in{'dev'} =~ /^tap/)) {
    $error .= $text{'error_network_bridge_device'}.'<BR>';
}

if ($in{'numberdev'} or $in{'numberdev'} == 0) {
    if ($in{'dev'} =~ /\d/) {
	$in{'dev'} =~ /\D(\d+)$/;
	my $num = $1; 
	$in{'dev'} =~ s/$num/$in{'numberdev'}/;
    } else {
	$in{'dev'} .= $in{'numberdev'};
    }
} elsif ($in{'modify'} == 1) {
    if ($in{'dev'} =~ /tun/) {
	$in{'dev'} = 'tun';
    } elsif ($in{'dev'} =~ /tap/) {
	$in{'dev'} = 'tap';
    }
}

if ($in{'dev'} =~ /tap/){
    $isstartpathcorrect = system("test -f ".$config{'br_start_cmd'});
    $isendpathcorrect = system("test -f ".$config{'br_end_cmd'});
    $ispluginpathcorrect = system("test -f ".$config{'br_start_cmd'});
    if (not ( ($isstartpathcorrect == 0 ) && ($isendpathcorrect == 0) && ($ispluginpathcorrect == 0) ) ){
	$error .= $text{'error_path_bridge'}.'<br>';
    }	
    if (($in{'iprangestart'} =~ /^$/) || ($in{'iprangeend'} =~ /^$/)) {
	$error .= $text{'error_ip_range_bridge'}.'<BR>';
    } else {
	if ($in{'iprangestart'} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) {
	    $error .= 'iprangestart <BR>';
	} else {
            $chk_res = check_ip_netmask("ip",$in{'iprangestart'});
            if ($chk_res =~ /false/) {
		$error .= $text{'error_ip_start_bridge'}.'<BR>';
	    }
	}
	if ($in{'iprangeend'} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) {
	    $error .= 'iprangeend.<BR>';
	} else {
            $chk_res = check_ip_netmask("ip",$in{'iprangeend'});
            if ($chk_res =~ /false/) {
                $error .= $text{'error_ip_end_bridge'}.'<BR>';
            }
	}
    }
    if (($in{'ipbr'} =~ /^$/) || ($in{'netmaskbr'} =~ /^$/)) {
	$error .= $text{'error_ip_netmask_bridge'}.'<BR>';
    } else {
	if ($in{'ipbr'} =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) {
            $chk_res = check_ip_netmask("ip",$in{'ipbr'});
            if ($chk_res =~ /false/) {
        	$error .= $text{'error_ip_bridge'}.'<BR>';
            }
	} else {
	    $error .= $text{'error_ip_notset_bridge'}.'<BR>';
	}	
	if ($in{'netmaskbr'} =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) {
	    $chk_res = check_ip_netmask("netmask",$in{'ipbr'});
	    if ($chk_res =~ /false/) {
		$error .= $text{'error_netmask_bridge'}.'<BR>';	
	    }	
	} else {
	    $error .= $text{'error_netmask_notset_bridge'}.'<BR>';
	}
    }
    if ($in{'network'}){
	$error .= &text('error_device', $text{'network'},$text{'new_vpn_server'}).'<BR>';
    }
    if ($in{'netmask'}){
	$error .= &text('error_device', $text{'netmask'},$text{'new_vpn_server'}).'<BR>';
    }
} elsif ($in{'dev'} =~ /tun/){
    if (($in{'iprangestart'} =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) || ($in{'iprangeend'} =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/)) {
	$error .= $text{'error_device_iprange'}.'<BR>';
    }
    if ($in{'devbr'}){
	$error .= $text{'error_device_bridge'}.'<BR>';
    }
    if (($in{'ipbr'} =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) || ($in{'netmaskbr'} =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/)) {
	$error .= $text{'error_device_netmask'}.'<BR>';
    }
}

if ($in{'management'} == 1) {
    if ($in{'management_port'} =~ /\D/) {
	$error .= $text{'error_management_port'}.'<BR>';
    } elsif ($in{'management_port'} < 1024 or $in{'management_port'} > 65535) {
	$error .= $text{'error_management_port_range'}.'<BR>';
    }
}

if ($in{'keepalive_ping'} and $in{'keepalive_ping-restart'}) {
    if ($in{'keepalive_ping'} =~ /\D/) {
	$error .= $text{'error_keepalive_ping'}.'<BR>';
    }
    if ($in{'keepalive_ping-restart'} =~ /\D/) {
	$error .= $text{'error_keepalive_ping-restart'}.'<BR>';
    }
}

if ($in{'max-clients'} == 0 or $in{'max-clients'} eq '') {
    delete($in{'max-clients'});
} elsif ($in{'max-clients'} =~ /\D/) {
    $error .= $text{'error_max-clients'}.'<BR>';
}

if ($in{'adds_conf'}) { $in{'adds_conf'} =~ s/\r+//g; }

if ($in{'dev'} =~ /tun/ and ($in{'network'} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/ or !$in{'network'})){
    $error .= $text{'error_network'}.'<BR>';
} elsif ($in{'dev'} =~ /tun/){
    $chk_res = check_ip_netmask("network",$in{'network'});
    if ($chk_res =~ /false/) { $error .= $text{'error_network'}.'<BR>'; }
} elsif ($in{'network'} && $in{'dev'} =~ /tap/) {
    $error .= $text{'error_tap_network'}.'<BR>';
}

if ($in{'dev'} =~ /tun/ and ($in{'netmask'} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/ or !$in{'netmask'})) {
    $error .= $text{'error_netmask'}.'<BR>';
} elsif ($in{'dev'} =~ /tun/){
    $chk_res = check_ip_netmask("netmask",$in{'netmask'});
    if ($chk_res =~ /false/) {
	$error .= $text{'error_netmask'}.'<BR>';
    }
} elsif ($in{'network'} && $in{'dev'} =~ /tap/){
    $error .= $text{'error_tap_netmask'}.'<BR>';
}

foreach $k (qw/fragment mssfix tun-mtu/) {
    if ($in{$k} and ($in{$k} < 100 or $in{$k} > 1500)) {
	$error .= $k.': '.$text{'error_mtu'}.'<BR>';
    }
}

if (-s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/'.$in{'choose_server'}.'.key' and -s $config{'openvpn_home'}.'/'.$in{'ca_dir'}.'/'.$in{'choose_server'}.'.crt') {
    # composti da choose_server
    $in{'key'} = $in{'ca_dir'}.'/'.$in{'choose_server'}.'.key';
    $in{'cert'} = $in{'ca_dir'}.'/'.$in{'choose_server'}.'.crt';
} else {
    $error .= $text{'error_choose_server'}.'<BR>';
}

# controllo utilizzo porta + proto + local + dev da altre VPN
# controllo che network non sia gia' utilizzata
opendir D, $config{'openvpn_home'};
@files = readdir D;
closedir D;

$in{'network'} =~ /^(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}$/;
$my_rete = $1;
@a_tapinuse = ();
@a_brinuse = ();
@a_ethinuse = ();

$tundevicesenzanumero = 0;
$tapdevicesenzanumero = 0;

%tundevices = ();
%tapdevices = ();

foreach $file (@files) {
    if ($file =~ /^$in{'VPN_NAME'}\./) { next; }
    if ($file =~ /^.+\.conf$/) {
	$file =~ /^(.+)\.conf$/;
	$server = $1;
    } elsif ($file =~ /^.+\.disabled$/) {
	$file =~ /^(.+)\.disabled$/;
	$server = $1;
    }
    if ($file =~ /^.+\.conf$/ or $file =~ /^.+\.disabled$/) {
	$ok_port = 0;
	$ok_proto = 0;
	$ok_management = 0;
	$ok_local = '';
	$ok_server = '';
	$ok_ifconfig = '';
	$ok_secret = 0;
	open F,$config{'openvpn_home'}.'/'.$file;
	while ($row=<F>) {
	    chomp($row);
	    if ($in{'management'} == 1 and $row =~ /^management\s+127\.0\.0\.1\s+$in{'management_port'}\s*$/) { $ok_management=1; }
	    if ($row =~ /^secret\s+/) { $ok_secret = 1; }
	    if ($row =~ /^port\s+$in{'port'}\s*$/) { $ok_port = 1; }
	    if ($row =~ /^proto\s+$in{'proto'}\s*$/) { $ok_proto = 1; }
#
#	if there are taps in use add the used taps to @a_tapinuse array to prevend overlaps
	    if ($row =~ /^dev\stap/) { 
		$tapdevice = $row;
		$tapdevice =~ s/^dev\s//;
		push (@a_tapinuse,$tapdevice);
	    }
	    if ($row =~ /^dev\s/) { 
		$tapdevice = $row;
		$tapdevice =~ s/^dev\s//;
		if ($tapdevice =~ /tun/) {
		    if ($tapdevice eq "tun") {
			$tundevicesenzanumero = 1;
		    } else {
			$tapdevice =~ /tun(\d+)/;    
			$tundevices{$1} = 1;
		    }
		} elsif ($tapdevice =~ /tap/) {
		    if ($tapdevice eq "tap") {
			$tapdevicesenzanumero = 1;
		    } else {
			$tapdevice =~ /tap(\d+)/;    
			$tapdevices{$1} = 1;
		    }
		}
	    }
	    
            if ($row =~ /^local\s+/) { $row =~ /^local\s+(.+)\s*$/; $ok_local = $1; }
	    if ($row =~ /^server\s+/) { $row =~ /^server\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.).+\s+.+\s*$/; $ok_server = $1; }
	    if (($row =~ /^server-bridge/) && ($in{'dev'} =~ /^tap/)){
		$srvbr = $row;
		$srvbr =~ s/^server-bridge\s//;
		$srvbr =~ s/\s+#@@//;
		@srvbr_ele = split(' ',$srvbr);
		if (($in{'devbr'} =~ /^$srvbr_ele[4]$/) && ($in{'ipbr'} !~ /^$srvbr_ele[0]$/ ))
		{
			$error .= &text('error_bridge_server_1', $server).'<BR>';
			$error .= &text('error_bridge_server_2', $in{'devbr'},$srvbr_ele[0]).'<BR>';
		}
		if (($in{'netdevbr'} eq $srvbr_ele[5]) && (($in{'devbr'} ne $srvbr_ele[4]) || ($in{'ipbr'} ne $srvbr_ele[0] ))){
			$error .= &text('error_bridge_server_3', $server).'<BR>';
		}
	   }
	    if ($row =~ /^ifconfig\s+/) { $row =~ /^ifconfig\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.).+\s+.+\s*$/; $ok_ifconfig = $1; }
	}
	close F;
	if ($ok_secret == 1) {
	    if ($ok_port == 1 and $ok_proto == 1) {
		$error .= $text{'error_port_used'}.' '.$server.'<BR>';
	    }
	    if (($ok_ifconfig eq $my_rete) &&  ( $my_rete !~ /^$/)) {
		$error .= $text{'error_network_used'}.' '.$server.'<BR>';
	    }
	} else {
	    if ($ok_port == 1 and $ok_proto == 1 and ($in{'local'} eq 'ALL' or $in{'local'} eq '')) {
		$error .= $text{'error_port_used'}.' '.$server.'<BR>';
	    } elsif (($in{'local'} ne 'ALL' and $in{'local'} ne '') and ($ok_local eq '' or $ok_local eq $in{'local'})) {
		$error .= $text{'error_port_used'}.' '.$server.'<BR>';
	    }
	    if (($ok_server eq $my_rete) && ( $my_rete !~ /^$/)) {
		$error .= $text{'error_network_used'}.' '.$server.'<BR>';
	    }
	}
	if ($ok_management == 1) {
	    $error .= $text{'error_management_port_used'}.' '.$server.'<BR>';
	}
    }
}

if ($in{'modify'} != 1 or !$in{'modify'} or !exists($in{'modify'})) {
    if ($in{'dev'} eq 'tun') {
	my $myvalue = 0;
	while (exists($tundevices{$myvalue})) {
	    $myvalue++;
	}
	$in{'dev'} .= $myvalue;
    } elsif ($in{'dev'} eq 'tap') {
	my $myvalue = 0;
	while (exists($tapdevices{$myvalue})) {
	    $myvalue++;
	}
	$in{'dev'} .= $myvalue;
    }
} else {
    if ($in{'dev'} =~ /tun/) {
	if (($in{'numberdev'} == 0 or $in{'numberdev'}) and exists($tundevices{$in{'numberdev'}}) or ($in{'numberdev'} eq "" and $tundevicesenzanumero == 1)) {
	    my $string = join(",tun",(keys %tundevices));
	    if ($tundevicesenzanumero == 1) { $string .= ",tun"; }
	    $error .= $text{'tun_or_tap_used'}.' tun'.$string.'<BR>';
	}
    } elsif ($in{'dev'} =~ /tap/) {
	if (($in{'numberdev'} == 0 or $in{'numberdev'}) and exists($tapdevices{$in{'numberdev'}}) or ($in{'numberdev'} eq "" and $tapdevicesenzanumero == 1)) {
	    my $string = join(",tap",(keys %tapdevices));
	    if ($tapdevicesenzanumero == 1) { $string .= ",tap"; }
	    $error .= $text{'tun_or_tap_used'}.' tap'.$string.'<BR>';
	}
    }
}

if ($in{'modify'} != 1) {
    # rimuovo directory se esistente
    if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}) {
	&system_logged("rm -rf ".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}." >/dev/null 2>&1 </dev/null");
    }
    # crea le directory per il server
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'},0755);
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'},0755);
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/logs',0755);
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/ccd',0755);
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin',0755);
}

# find the next unused tap device and set $in{'dev'}
if ($in{'dev'} =~ /tap/){
    my $devicenumber = 0;
    my $temptapdev = ();
    my $deviceinuse = 0;
    #@a_tapinuse = [];
    
    &open_execute_command(CMD, 'ifconfig|grep -E "^tap" |awk \'{print $1}\'', 2);
    while ($row=<CMD>) {
	$row =~ s/\r*\n//g;
	push (@a_tapinuse,$row);	
    }
    close(CMD);
    do
    {
	$count = 0;
	$temptapdev = 'tap'.$devicenumber;
	foreach(@a_tapinuse){
	    if ($temptapdev eq $_) { $count++; }
	}
	if ($count > 0){
	    $devicenumber = $devicenumber + 1;
	} else{
	    $deviceinuse = 1;
	}
    } while ($deviceinuse eq 0);
   $in{'dev'} = $temptapdev;
}

# array of aviable ethernet devices
$a_eth = &ReadEths($in{'devbr'});
#$a_eth = [];
#&open_execute_command(CMD, 'ifconfig|grep -i :ethernet |awk \'{print $1}\'', 2);
#while ($row=<CMD>) {
#    $row =~ s/\r*\n//g;
#    if (($row ne $in{'devbr'}) && ($row !~ /^tap\d+/)) {
#	push(@$a_eth,[$row,$row]);
#    }
#}
#close(CMD);

# generate our bridge commands
if ($in{'dev'} =~ /^tap/){
    $bridgestart_cmd = $config{'br_start_cmd'}.' --setbr br='.$in{'devbr'}.' eth='.$in{'netdevbr'}.' tap='.$in{'dev'}.' ip='.$in{'ipbr'}.' netmask='.$in{'netmaskbr'}.' > /dev/null';
    $bridgeend_cmd = $config{'br_end_cmd'}.' --killbridge --seteth br='.$in{'devbr'}.' eth='.$in{'netdevbr'}.' tap='.$in{'dev'}.' ip='.$in{'ipbr'}.' netmask='.$in{'netmaskbr'}.' > /dev/null';
#    $in{'down-root'} = '## DO NOT MODIFY ##';
}

# some vars 'needed' to generate the up/down/up-pre/down-pre/down-root scripts
$bash_shebang = "#!/bin/bash";
$usrscript_border = "##### add your commands below #####";

#chiavi per comandi attivazione/disattivazione
foreach $k (qw/up down up-pre down-pre down-root/) {
    if ($in{'modify'}) {
        if (-f $config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k) { unlink($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k); }
    }
    
    # if no up|down user commands are entered, but we have a tap-device, $in{$k} is set to a command
    if(($k =~ /^up$/ || $k =~ /^down-root$/) && (!$in{$k}) && ($in{'dev'} =~ /^tap/)){
	$in{$k} = '### Add your commands here ###';
    }

    if ($in{$k}) {
        $in{$k} =~ s/\r+//g;
        open U,">".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k;

	# sometimes 'file' fails to check the file type
	# bash-shebang added as workaround
        print U $bash_shebang."\n\n";
	
	# if tap is selected add our bridge start/end command to up/down script
	if (($in{'dev'} =~ /^tap/) && ($k =~ /up/)){
		print U $bridgestart_cmd."\n\n";
	}elsif (($in{'dev'} =~ /^tap/) && ($k =~ /down-root/)){
		print U $bridgeend_cmd."\n\n";
	}
	
	# add border between our and the user commands
	print U $usrscript_border."\n";
	# the user commands are added to the script
	print U $in{$k};
        close U;
        chmod(0755,$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k);
    }
}

# rieseguo la schermata di new con i campi riempiti dai valori inseriti 
# ed il messaggio di errore
if ($error) {

    &ReadFieldsCA($in{'ca_name'});

    $a_verb = [];
    for ($i=1;$i<=15;$i++) { push(@$a_verb,[$i,$i]); }

    $a_mute = [ [ 0, $text{'unassigned'} ] ];
    for ($i=10;$i<=50;$i=$i+10) { push(@$a_mute,[$i,$i]); }

    &foreign_require("useradmin", "user-lib.pl");

    # utenti di sistema
    $a_user = [];
    @users = &useradmin::list_users();
    @users = &useradmin::sort_users(\@users, 1);
    foreach $us (@users) {
	push @$a_user,[$$us{'user'},$$us{'user'}];
    }

    # gruppi di sistema
    $a_group = [];
    @groups = &useradmin::list_groups();
    @groups = &useradmin::sort_groups(\@groups, 1);
    foreach $us (@groups) {
	push @$a_group,[$$us{'group'},$$us{'group'}];
    }

    # array derivante da comando 'openvpn --show-ciphers': il valore e' il primo campo ed etichetta tutto
    $a_cypher = &ReadCiphers();
#    $a_cypher = [];
#    &open_execute_command(CMD, $config{'openvpn_path'} . ' --show-ciphers', 2);
#    while ($row=<CMD>) {
#	$row =~ s/\r*\n//g;
#	if (($row =~ /bit default key/i) or ($row =~ /bit key,/i) or ($row =~ /bit key by default,/i)) {
#	    ($key) = split(' ',$row);
#	    push(@$a_cypher,[$key,$row]);	
#	}
#    }
#    close(CMD);

    # estrarre elenco chiavi server [della ca selezionata]
    $a_server = &ReadCAKeys($in{'ca_name'},2,1);

    # intestazione pagina
    &ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

    print "<BR>";
    print '<P><SPAN STYLE="color:red">'.$error.'</SPAN></P>';
    print "<BR>";

    $in{'dev'} =~ s/^tap\d/tap/;

    # form per nuova VPN
    print &ui_form_start("create_vpn.cgi", "POST");
    print &ui_hidden('ca_dir',$in{'ca_dir'});
    print &ui_hidden('ca',$in{'ca'});
    print &ui_hidden('ca_name',$in{'ca_name'});
    print &ui_hidden('management_url','127.0.0.1');
    print &ui_hidden('dh',$in{'dh'});
    print &ui_hidden('ccd-exclusive',1);
    print &ui_hidden('modify',$in{'modify'});
    print &ui_hidden('crl-verify',$in{'crl-verify'});
    if ($in{'modify'} == 1) {
	print &ui_hidden('VPN_NAME',$in{'VPN_NAME'});
	print &ui_hidden('port',$in{'port'});
	print &ui_table_start($text{'modifyvpn_server_title'});
	print &ui_table_row($text{'name'}, $in{'VPN_NAME'},'',[ 'width="50%"' ])."</tr>\n";
	print "<tr>".&ui_table_row($text{'port'}, $in{'port'},'',[ 'width="50%"' ])."</tr>\n";
    } else {
	print &ui_table_start($text{'newvpn_server_title'});
	print &ui_table_row($text{'name'}, &ui_textbox('VPN_NAME',$in{'VPN_NAME'},50),'',[ 'width="50%"' ])."</tr>\n";
	print "<tr>".&ui_table_row($text{'port'}, &ui_textbox('port',$in{'port'},50),'',[ 'width="50%"' ])."</tr>\n";
    }
    print "<tr>".&ui_table_row($text{'protocol'}, &ui_select('proto', $in{'proto'}, [ ['udp','udp'],['tcp-server','tcp-server'],['tcp-client','tcp-client'] ]),'',[ 'width="50%"' ])."</tr>\n";
    if ($in{'modify'} == 1) {
	$in{'dev'} =~ /^(\D*)(\d*)$/;
	$dev = $1;
	$numberdev = $2;
	print "<tr>".&ui_table_row($text{'dev'}, &ui_hidden('dev',$in{'dev'}).$dev." ".&ui_textbox('numberdev', $numberdev, 6),'',[ 'width="50%"' ])."</tr>\n";
    } else {
	print "<tr>".&ui_table_row($text{'dev'}, &ui_select('dev', $in{'dev'}, [ ['tun','tun'],['tap','tap'] ]))."</tr>\n";
    }

##############################
##############################
    if ($in{'modify'} == 1 and $dev and $dev eq 'tap') { print bridge_control_elements(); }
##############################
##############################

    print "<tr>".&ui_table_row($text{'management'}, $text{'management_enable'}.': '.&ui_select('management', $in{'management'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]).' '.$text{'management_url'}.': 127.0.0.1 '.$text{'management_port'}.': '.&ui_textbox('management_port',$in{'management_port'},5),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'ca'}, $in{'ca_name'})."</tr>\n";
    if (@{$a_server}) { 
	print "<tr>".&ui_table_row($text{'choose_server'}, &ui_select('choose_server', $in{'choose_server'}, $a_server),'',[ 'width="50%"' ])."</tr>\n";
    } else {
	print "<tr>".&ui_table_row($text{'choose_server'}, "<span style='color:red'>".$text{'list_keys_server_empty'}."</span>",'',[ 'width="50%"' ])."</tr>\n";
    }
    print "<tr>".&ui_table_row($text{'cert_server'}, $text{'automatic'},'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'key_server'}, $text{'automatic'},'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'dh'}, 'dh'.$$info_ca{'KEY_SIZE'}.'.pem')."</tr>\n";
    print "<tr>".&ui_table_row($text{'tls-server'}, &ui_select('tls-server', $in{'tls-server'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'local'}, &ui_textbox('local',$in{'local'},50),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'new_vpn_server'}, $text{'network'}.''.&ui_textbox('network',$in{'network'},15)." ".$text{'netmask'}.''.&ui_textbox('netmask',$in{'netmask'},15),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'ifconfig-pool-persist'}, &ui_select('ifconfig-pool-persist', $in{'ifconfig-pool-persist'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'client-to-client'}, &ui_select('client-to-client', $in{'client-to-client'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'duplicate-cn'}, &ui_select('duplicate-cn', $in{'duplicate-cn'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'tls-auth'}, &ui_select('tls-auth', $in{'tls-auth'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'ccd-exclusive'}, $text{'yes'},'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'cipher'}, &ui_select('cipher', $in{'cipher'}, $a_cypher),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'comp-lzo'}, &ui_select('comp-lzo', $in{'comp-lzo'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'max-clients'}, &ui_textbox('max-clients',$in{'max-clients'},4),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'user'}, &ui_select('user', $in{'user'}, $a_user),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'group'}, &ui_select('group', $in{'group'}, $a_group),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'persist-key'}, &ui_select('persist-key', $in{'persist-key'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'persist-tun'}, &ui_select('persist-tun', $in{'persist-tun'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'keepalive'}, $text{'keepalive_ping'}.': '.&ui_textbox('keepalive_ping',$in{'keepalive_ping'},3)." ".$text{'keepalive_ping-restart'}.': '.&ui_textbox('keepalive_ping-restart',$in{'keepalive_ping-restart'},3),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'verb'}, &ui_select('verb', $in{'verb'}, $a_verb),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'mute'}, &ui_select('mute', $in{'mute'}, $a_mute),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'status'}, 'openvpn-status.log')."</tr>\n";
    print "<tr>".&ui_table_row($text{'log-append'}, 'openvpn.log')."</tr>\n";
    print "<tr>".&ui_table_row($text{'tun-mtu'}, &ui_textbox('tun-mtu',$in{'tun-mtu'},4),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'fragment'}, &ui_textbox('fragment',$in{'fragment'},4),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'mssfix'}, &ui_textbox('mssfix',$in{'mssfix'},4),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'float'}, &ui_select('float', $in{'float'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'chroot'}.' '.$config{'openvpn_home'}, &ui_select('chroot', $in{'chroot'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'topology'}, &ui_select('topology', $in{'topology'}, [ ['subnet',$text{'subnet'}],['p2p',$text{'p2p'}], ['net30',$text{'net30'}] ]),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'adds_conf'}, &ui_textarea('adds_conf', $in{'adds_conf'}, 5, 45, 'off'),'',[ 'width="50%"' ])."</tr>\n";
    print &ui_table_end();
    print &ui_table_start($text{'commands'},'width=100%');
    print "<tr>".&ui_table_row($text{'up-pre'}, &ui_textarea('up-pre', $in{'up-pre'}, 3, 45, 'off'),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'up'}, &ui_textarea('up', $in{'up'}, 3, 45, 'off'),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'down-pre'}, &ui_textarea('down-pre', $in{'down-pre'}, 3, 45, 'off'),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'down'}, &ui_textarea('down', $in{'down'}, 3, 45, 'off'),'',[ 'width="50%"' ])."</tr>\n";
    print "<tr>".&ui_table_row($text{'down-root'}, &ui_textarea('down-root', $in{'down-root'}, 3, 45, 'off'),'',[ 'width="50%"' ])."</tr>\n";
    print &ui_table_end();
    print &ui_form_end([ [ "save", $text{'save'} ] ]);

    print "<BR><BR>";

    #footer della pagina
    &footer("listvpn.cgi", $text{'listserver_title'});

} else {
    # modifica vpn
    if ($in{'tls-auth-old'}) {
	if ($in{'tls-auth'} == 1) {
	    if ($in{'tls-auth-old'} !~ /\/$in{'VPN_NAME'}\//) {
		File::Copy::copy($config{'openvpn_home'}.'/'.$in{'tls-auth-old'},$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/ta.key');
	    }
	    $in{'tls-auth'} = $config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/ta.key 0';
	} else { 
	    unlink($config{'openvpn_home'}.'/'.$in{'tls-auth-old'});
	    delete($in{'tls-auth'}); 
	}
    # nuova vpn
    } else {
	if ($in{'tls-auth'} == 1) {
	    if (!-f $config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/ta.key') {
		&system_logged($config{'openvpn_path'}." --genkey --secret ".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/ta.key'." >/dev/null 2>&1 </dev/null");
		chmod(0644,$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/ta.key');
	    }
	    $in{'tls-auth'} = $config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/ta.key 0';
	} else { delete($in{'tls-auth'}); }
    }

    if ($in{'dev'} =~ /tun/){
    	$in{'server'} = $in{'network'}.' '.$in{'netmask'}; 
    }
    if ($in{'dev'} =~ /tap\d/){
    	$in{'server-bridge'} = $in{'ipbr'}.' '.$in{'netmaskbr'}.' '.$in{'iprangestart'}.' '.$in{'iprangeend'}.' #@@ '.$in{'devbr'}.' '.$in{'netdevbr'};
    }
    $in{'status'} = $config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/logs/openvpn-status.log';
    $in{'log-append'} = $config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/logs/openvpn.log';
    if ($in{'ifconfig-pool-persist'} == 1) {
	$in{'ifconfig-pool-persist'} = $config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/logs/ipp.txt';
    } else {
	delete($in{'ifconfig-pool-persist'});
    }

    if ($in{'modify'} == 1) {
	if (-s $config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.'.conf') {
	    $namefile = $config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.'.conf';
	} elsif (-s $config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.'.disabled') {
    	    $namefile = $config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.'.disabled';
	}
	open OUT, ">".$namefile;
    } else {
	# scrivo file di configurazione server
	open OUT,">".$config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.".conf";
    }

    if ($in{'dev'} =~ /tun/){
    	foreach $k (qw/port proto dev ca cert key dh topology server crl-verify/) {
	    if ($in{$k}) { print OUT $k.' '.$in{$k}."\n"; }
    	}
    }elsif ($in{'dev'} =~ /tap/){
    	foreach $k (qw/port proto dev ca cert key dh topology server-bridge crl-verify/) {
	    if ($in{$k}) { print OUT $k.' '.$in{$k}."\n"; }
    	}
    }
	
    foreach $k (qw/ifconfig-pool-persist tls-auth cipher user group status log-append verb mute/) {
	if (exists($in{$k})) { print OUT $k.' '.$in{$k}."\n"; }
    }

    foreach $k (qw/max-clients tun-mtu fragment mssfix/) {
	if ($in{$k} and exists($in{$k})) { print OUT $k.' '.$in{$k}."\n"; }
    }

    # se ALL non scrivo la chiave
    if ($in{'local'} ne 'ALL' and $in{'local'} ne '') { print OUT 'local '.$in{'local'}."\n"; }

    if ($in{'management'} == 1) { print OUT 'management '.$in{'management_url'}.' '.$in{'management_port'}."\n"; }

    if ($in{'keepalive_ping'} and $in{'keepalive_ping-restart'}) { print OUT 'keepalive '.$in{'keepalive_ping'}.' '.$in{'keepalive_ping-restart'}."\n"; }

    if ($in{'ccd-exclusive'} == 1) {
	if ($in{'chroot'} == 1) {
	    print OUT 'client-config-dir '.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}."/ccd\n";
	} else {
	    print OUT 'client-config-dir '.$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}."/ccd\n";
	}
    }

    # se 1 allora scrivo solo la chiave altrimenti non la scrivo
    foreach $k (qw/tls-server client-to-client duplicate-cn comp-lzo persist-key persist-tun float ccd-exclusive/) {
	if ($in{$k} == 1) { print OUT $k."\n"; }
    }

    if ($in{'chroot'} == 1) { print OUT 'chroot '.$config{'openvpn_home'}."\n"; }
    
    # chiavi per comandi attivazione/disattivazione
    foreach $k (qw/up down up-pre down-pre/) {
	if ($in{$k}) { print OUT $k.' '.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k."\n"; }
    }
    
    if ($in{'down-root'}) {
	print OUT 'plugin '.$config{'down_root_plugin'}.' "'.$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.down-root"'."\n"; 
    }

     if ($in{'adds_conf'}) { print OUT $in{'adds_conf'}."\n"; }

    close OUT;

    &redirect("listvpn.cgi");
}
