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

$error = "";

if (($in{'VPN_NAME'} !~ /^[a-zA-Z0-9_\-\.]{4,}$/) or ($in{'VPN_NAME'} =~ /\.{2,}/) or ($in{'VPN_NAME'} =~ /\.$/)){
    $error .= $text{'error_vpn_notok'}.' $&<BR>';
} elsif (-s $config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.'.conf' and $in{'modify'} != 1) {
    $error .= $text{'error_vpn_exist'}.'<BR>';
}

if ($in{'vpn_port'} =~ /\D/ or $in{'client_port'} =~ /\D/) {
    $error .= $text{'error_port'}.'<BR>';
}

if ($in{'client_remote_port'} =~ /\D/) {
    $error .= $text{'error_client_remote_port'}.'<BR>';
}
if ($in{'client_remote_url'} !~ /.{4}/) {
    $error .= $text{'error_client_remote_url'}.'<BR>';
}

if ($in{'client-nat'} == 0) {
    if ($in{'vpn_remote_port'} =~ /\D/) {
	$error .= $text{'error_vpn_remote_port'}.'<BR>';
    }
    if ($in{'vpn_remote_url'} !~ /.{4}/) {
	$error .= $text{'error_vpn_remote_url'}.'<BR>';
    }
}

if ($in{'vpn_keepalive_ping'} and $in{'vpn_keepalive_ping-restart'}) {
    if ($in{'vpn_keepalive_ping'} =~ /\D/) {
	$error .= $text{'error_keepalive_ping'}.'<BR>';
    }
    if ($in{'vpn_keepalive_ping-restart'} =~ /\D/) {
	$error .= $text{'error_keepalive_ping-restart'}.'<BR>';
    }
}

if ($in{'client_adds_conf'}) { $in{'client_adds_conf'} =~ s/\r+//g; }
if ($in{'vpn_adds_conf'}) { $in{'vpn_adds_conf'} =~ s/\r+//g; }

if ($in{'vpn_ifconfig_from'} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) {
    $error .= $text{'error_ifconfig_from'}.'<BR>';
} else {
    @part_ip = split('.',$in{'vpn_ifconfig_from'});
    foreach $p ( @part_ip ) {
	if ($p < 0 or $p > 255) {
	    $error .= $text{'error_ifconfig_from'}.'<BR>';
	    last;
	}
    }
}

if ($in{'vpn_ifconfig_to'} !~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) {
    $error .= $text{'error_ifconfig_to'}.'<BR>';
} else {
    @part_ip = split('.',$in{'vpn_ifconfig_to'});
    foreach $p ( @part_ip ) {
	if ($p < 0 or $p > 255) {
	    $error .= $text{'error_ifconfig_to'}.'<BR>';
	    last;
	}
    }
}


if ($in{'management'} == 1) {
    if ($in{'management_port'} =~ /\D/) {
        $error .= $text{'error_management_port'}.'<BR>';
    } elsif ($in{'management_port'} < 1024 or $in{'management_port'} > 65535) {
        $error .= $text{'error_management_port_range'}.'<BR>';
    }
}

$in{'vpn_ifconfig_to'} =~ /^(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}$/;
$myto=$1;    

$in{'vpn_ifconfig_from'} =~ /^(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}$/;
$my_rete = $1;

if ($my_rete ne $myto) {
    $error .= $text{'error_ifconfig'}.'<BR>';
}

# controllo utilizzo porta + proto da altre VPN
# controllo che network non sia gia' utilizzata
opendir D, $config{'openvpn_home'};
@files = readdir D;
closedir D;

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
	$ok_server = '';
	$ok_ifconfig = '';
	$ok_secret = 0;
	open F,$config{'openvpn_home'}.'/'.$file;
	while ($row=<F>) {
	    chomp($row);
	    if ($in{'management'} == 1 and $row =~ /^management\s+127\.0\.0\.1\s+$in{'management_port'}\s*$/) { $ok_management=1; }
	    if ($row =~ /^secret\s+/) { $ok_secret = 1; }
	    if ($row =~ /^port\s+$in{'vpn_port'}\s*$/) { $ok_port = 1; }
	    if ($row =~ /^proto\s+$in{'vpn_proto'}\s*$/) { $ok_proto = 1; }
	    if ($row =~ /^server\s+/) { $row =~ /^server\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.).+\s+.+\s*$/; $ok_server = $1; }
	    if ($row =~ /^ifconfig\s+/) { $row =~ /^ifconfig\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.).+\s+.+\s*$/; $ok_ifconfig = $1; }
	}
	close F;
	if ($ok_port == 1 and $ok_proto == 1) {
	    $error .= $text{'error_port_used'}.' '.$server.'<BR>';
	}
	if ($ok_secret == 1) {
	    if ($ok_ifconfig eq $my_rete) {
		$error .= $text{'error_ifconfig_from_used'}.' '.$server.'<BR>';
	    }
	} else {
	    if ($ok_server eq $my_rete) {
		$error .= $text{'error_ifconfig_from_used'}.' '.$server.'<BR>';
	    }
	}
	if ($ok_management == 1) {
	    $error .= $text{'error_management_port_used'}.' '.$server.'<BR>';
	}
    }
}

if ($in{'modify'} != 1) {
    # rimuovo directory se esistente
    if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}) {
	&system_logged("rm -rf ".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}." >/dev/null 2>&1 </dev/null");
    }
    # rimuovo directory se esistente
    if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}) {
	&system_logged("rm -rf ".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}." >/dev/null 2>&1 </dev/null");
    }
    # crea le directory per il server
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'},0755);
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'},0755);
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/logs',0755);
    mkdir($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin',0755);

}

# chiavi per comandi attivazione/disattivazione
foreach $k (qw/up down/) {
    if ($in{'modify'}) {
	if (-f $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.'.'.$k) { unlink($config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.'.'.$k); }
	if (-f $config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.'.'.$k) { unlink($config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.'.'.$k); }
    }
    if ($in{"vpn_".$k}) {
	$in{"vpn_".$k} =~ s/\r+//g;
	open U,">".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k;
	print U $in{"vpn_".$k};
	close U;
	chmod(0755,$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k);
	&execute_command("file ".$config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k, \$out, \$out);
	if ($out !~ /shell script text executable/i) {	
	    $error .= $text{'error_commands'}.' '.$k.'<BR>';
	}
    }
    if ($in{"client_".$k}) {
	$in{"client_".$k} =~ s/\r+//g;
	open U,">".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.'.'.$k;
	print U $in{"client_".$k};
	close U;
	chmod(0700,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.'.'.$k);
    }
}

# rieseguo la schermata di new con i campi riempiti dai valori inseriti 
# ed il messaggio di errore
if ($error) {

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

    # intestazione pagina
    &ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

    print "<BR>";
    print '<P><SPAN STYLE="color:red">'.$error.'</SPAN></P>';
    print "<BR>";


    # form per nuova VPN
    print &ui_form_start("create_static_vpn.cgi", "POST");	
    print &ui_hidden('modify',$in{'modify'});
    print &ui_hidden('management_url','127.0.0.1');
    if ($in{'modify'} == 1) {
	print &ui_hidden('VPN_NAME',$in{'VPN_NAME'});
	print &ui_hidden('vpn_port',$in{'vpn_port'});
	print &ui_table_start($text{'modifyvpn_static_title'});
    } else {
	print &ui_table_start($text{'newvpn_static_title'});
    }
    # th row
    print "<tr><td>";
    print &ui_table_start();
    print "<tr $tb>";
	print "<td valign=top><b>&nbsp;</b></td>\n";
	print "<td valign=top nowrap><b>".$text{'server'}."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'client'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
    print "<td valign=top><b>".$text{'name'}."</b></td>\n";
    if ($in{'modify'} == 1) {
	print "<td valign=top nowrap><b>".$in{'VPN_NAME'}."</b></td>\n";
    } else {
	print "<td valign=top nowrap><b>".&ui_textbox('VPN_NAME',$in{'VPN_NAME'},35)."</b></td>\n";
    }
    print "<td valign=top nowrap><b>&nbsp;</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'port'}."</b></td>\n";
	if ($in{'modify'} == 1) {
	    print "<td valign=top nowrap><b>".$in{'vpn_port'}."</b></td>\n";
	} else {
	    print "<td valign=top nowrap><b>".&ui_textbox('vpn_port',$in{'vpn_port'},35)."</b></td>\n";
	}
        print "<td valign=top nowrap><b>".&ui_textbox('client_port',$in{'client_port'},35)."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'protocol'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('vpn_proto', $in{'vpn_proto'}, [ ['udp','udp'],['tcp-server','tcp-server'],['tcp-client','tcp-client'] ])."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'dev'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('vpn_dev', $in{'vpn_dev'}, [ ['tun','tun'] ])."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'ifconfig'}."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'from'}.':'.&ui_textbox('vpn_ifconfig_from',$in{'vpn_ifconfig_from'},15)." ".$text{'to'}.':'.&ui_textbox('vpn_ifconfig_to',$in{'vpn_ifconfig_to'},15)."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'comp-lzo'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('vpn_comp-lzo', $in{'vpn_comp-lzo'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ])."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'remote'}."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'h_url'}.' '.&ui_textbox('vpn_remote_url',$in{'vpn_remote_url'},15).' '.$text{'h_port'}.': '.&ui_textbox('vpn_remote_port',$in{'vpn_remote_port'},5)."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'h_url'}.' '.&ui_textbox('client_remote_url',$in{'client_remote_url'},15).' '.$text{'h_port'}.': '.&ui_textbox('client_remote_port',$in{'client_remote_port'},5)."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'client-nat'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('client-nat', $in{'client-nat'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ])."</b></td>\n";
        print "<td valign=top nowrap><b>&nbsp;</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'management'}."</b></td>\n";
	print "<td valign=top nowrap><b>".$text{'management_enable'}.': '.&ui_select('management', $in{'management'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]).' '.$text{'management_url'}.': 127.0.0.1 '.$text{'management_port'}.': '.&ui_textbox('management_port',$in{'management_port'},5)."</b></td>\n";
	print "<td valign=top nowrap><b>&nbsp;</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'user'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('vpn_user', $in{'vpn_user'}, $a_user)."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'group'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('vpn_group', $in{'vpn_group'}, $a_group)."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'persist-key'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('vpn_persist-key', $in{'vpn_persist-key'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ])."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'persist-tun'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('vpn_persist-tun', $in{'vpn_persist-tun'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ])."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'keepalive'}."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'keepalive_ping'}.': '.&ui_textbox('vpn_keepalive_ping',$in{'vpn_keepalive_ping'},3)." ".$text{'keepalive_ping-restart'}.': '.&ui_textbox('vpn_keepalive_ping-restart',$in{'vpn_keepalive_ping-restart'},3)."</b></td>\n";
        print "<td valign=top nowrap><b>".$text{'automatic'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'verb'}."</b></td>\n";
	print "<td valign=top nowrap><b>".&ui_select('vpn_verb', $in{'vpn_verb'}, $a_verb)."</b></td>\n";
	print "<td valign=top nowrap><b>".&ui_select('client_verb', $in{'client_verb'}, $a_verb)."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'mute'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('vpn_mute', $in{'vpn_mute'}, $a_mute)."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_select('client_mute', $in{'client_mute'}, $a_mute)."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'status'}."</b></td>\n";
	print "<td valign=top nowrap><b>".'openvpn-status.log'."</b></td>\n";
        print "<td valign=top nowrap><b>&nbsp;</b></td>\n";
    print "</tr>\n";
    print "<tr>";
	print "<td valign=top><b>".$text{'log-append'}."</b></td>\n";
	print "<td valign=top nowrap><b>".'openvpn.log'."</b></td>\n";
	print "<td valign=top nowrap><b>&nbsp;</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'adds_conf'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_textarea('vpn_adds_conf', $in{'vpn_adds_conf'}, 5, 35, 'off')."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_textarea('client_adds_conf', $in{'client_adds_conf'}, 5, 35, 'off')."</b></td>\n";
    print "</tr>\n";
    print &ui_table_end();
    print &ui_table_start($text{'commands'});
    print "<tr><td>\n";
    print &ui_table_start();
    # th row
    print "<tr $tb>";
	print "<td valign=top><b>&nbsp;</b></td>\n";
	print "<td valign=top nowrap><b>".$text{'server'}."</b></td>\n";
	print "<td valign=top nowrap><b>".$text{'client'}."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'up'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_textarea('vpn_up', $in{'vpn_up'}, 5, 35, 'off')."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_textarea('client_up', $in{'client_up'}, 5, 35, 'off')."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
        print "<td valign=top><b>".$text{'down'}."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_textarea('vpn_down', $in{'vpn_down'}, 5, 35, 'off')."</b></td>\n";
        print "<td valign=top nowrap><b>".&ui_textarea('client_down', $in{'client_down'}, 5, 35, 'off')."</b></td>\n";
    print "</tr>\n";
    print "<tr>";
    	print "<td valign=top><b>" . $text{'statickey'} . "</b></td>\n";
    	print "<td valign=top nowrap><b>".&ui_textarea('static_key', $in{'static_key'}, 20, 35, 'off')."</b></td>\n";
    	print "<td><b>&nbsp;</b></td>\n";
    print "</tr>\n";

    print &ui_table_end();
    print &ui_form_end([ [ "save", $text{'save'} ] ]);

    print "<BR><BR>";

    #footer della pagina
    &footer("listvpn.cgi", $text{'listserver_title'});

} else {
    
    $in{'client_remote'} = $in{'client_remote_url'}.' '.$in{'client_remote_port'};
    if ($in{'client-nat'} == 0) { $in{'vpn_remote'} = $in{'vpn_remote_url'}.' '.$in{'vpn_remote_port'}; } else { delete($in{'vpn_remote'}); }
    $in{'vpn_status'} = $config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/logs/openvpn-status.log';
    $in{'vpn_log-append'} = $config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/logs/openvpn.log';
    $in{'vpn_ifconfig'} = $in{'vpn_ifconfig_from'}.' '.$in{'vpn_ifconfig_to'};
    $in{'client_ifconfig'} = $in{'vpn_ifconfig_to'}.' '.$in{'vpn_ifconfig_from'};
    if ($in{'vpn_keepalive_ping'} and $in{'vpn_keepalive_ping-restart'}) { $in{'vpn_keepalive'} = $in{'vpn_keepalive_ping'}.' '.$in{'vpn_keepalive_ping-restart'}; }
    else { delete($in{'vpn_keepalive'}); }

    if ( $in{'static_key'} ) {
       $secretfile = $config{'openvpn_home'}.'/'. $in{'VPN_NAME'} . ".key"; 
    	open FILE, ">" . $secretfile;
        print FILE $in{'static_key'};
	close FILE; 
    }
    else {
    	&system_logged($config{'openvpn_path'}." --genkey --secret ".$config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.'.key'." >/dev/null 2>&1 </dev/null");
    }
    	chmod(0644,$config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.".key");
    	File::Copy::copy($config{'openvpn_home'}.'/'.$in{'VPN_NAME'}.".key",$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.".key");
    $in{'vpn_secret'} = $in{'VPN_NAME'}.'.key';

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
    open CLI,">".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.'.conf';
    open WCLI,">".$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$in{'VPN_NAME'}.'/'.$in{'VPN_NAME'}.'.ovpn';

    foreach $k (qw/port remote ifconfig verb mute/) {
	if (exists($in{"vpn_".$k})) { print OUT $k.' '.$in{"vpn_".$k}."\n"; }
	if (exists($in{"client_".$k})) { 
	    print CLI $k.' '.$in{"client_".$k}."\n";
	    print WCLI $k.' '.$in{"client_".$k}."\n";
	}
    }

    foreach $k (qw/secret proto dev user group keepalive/) {
	if (exists($in{"vpn_".$k})) { 
	    print OUT $k.' '.$in{"vpn_".$k}."\n"; 
	    print CLI $k.' '.$in{"vpn_".$k}."\n"; 
	    if ($k eq "user" or $k eq "group") {
		print WCLI ';'.$k.' '.$in{"vpn_".$k}."\n"; 
	    } else {
		print WCLI $k.' '.$in{"vpn_".$k}."\n"; 
	    }
	}
    }

    if ($in{'management'} == 1) { print OUT 'management '.$in{'management_url'}.' '.$in{'management_port'}."\n"; }

    foreach $k (qw/status log-append/) {
	print OUT $k.' '.$in{"vpn_".$k}."\n";
    }

    # se 1 allora scrivo solo la chiave altrimenti non la scrivo
    foreach $k (qw/comp-lzo persist-key persist-tun/) {
	if ($in{"vpn_".$k} == 1) { 
	    print OUT $k."\n"; 
	    print CLI $k."\n"; 
	    print WCLI $k."\n"; 
	}
    }

    # chiavi per comandi attivazione/disattivazione
    foreach $k (qw/up down/) {
	if ($in{"client_".$k}) { 
	    print CLI $k.' '.$in{'VPN_NAME'}.'.'.$k."\n"; 
	    print WCLI $k.' '.$in{'VPN_NAME'}.'.'.$k."\n"; 
	}
	if ($in{"vpn_".$k}) { 
	    print OUT $k.' '.$config{'openvpn_servers_subdir'}.'/'.$in{'VPN_NAME'}.'/bin/'.$in{'VPN_NAME'}.'.'.$k."\n"; 
	}
    }

    if ($in{'vpn_adds_conf'}) { print OUT $in{'vpn_adds_conf'}."\n"; }
    if ($in{'client_adds_conf'}) { 
	print CLI $in{'client_adds_conf'}."\n"; 
	print WCLI $in{'client_adds_conf'}."\n"; 
    }

    close OUT;
    close CLI;
    close WCLI;

    #footer della pagina
    &redirect("listvpn.cgi");
}
