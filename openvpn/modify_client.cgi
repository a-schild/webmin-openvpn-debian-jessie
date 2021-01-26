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

%client_info = %in;
%in = ( 'vpn' => $client_info{'vpn'});
&ReadVPNConf();

$tlsauth_server = $in{'tls-auth'};
delete($in{'tls-auth'});

%server_info = %in;

%in = %client_info;

&ReadClientConf();

$in{'CLIENT_NAME'} = $in{'client'};

&ReadFieldsCA($in{'CA_NAME'});

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

# estrarre elenco chiavi client [della ca selezionata]
$a_clients = &ReadCAKeys($in{'CA_NAME'},3,1,1);

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
            &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
            undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";
print '<P><SPAN STYLE="color:red">'.$error.'</SPAN></P>';
print "<BR>";

# form per nuova VPN
print &ui_form_start("create_client.cgi", "POST");
print &ui_hidden('ca_dir',$config{'openvpn_keys_subdir'}.'/'.$$info_ca{'CA_NAME'});
print &ui_hidden('ca','ca.crt');
print &ui_hidden('ca_name',$$info_ca{'CA_NAME'});
print &ui_hidden('vpn',$in{'vpn'});
print &ui_hidden('tun-mtu',$in{'tun-mtu'});
print &ui_hidden('mssfix',$in{'mssfix'});
print &ui_hidden('dev',$in{'dev'});
print &ui_hidden('proto',$in{'proto'});
print &ui_hidden('client',$in{'CLIENT_NAME'});
print &ui_hidden('remote_port',$in{'remote_port'});
print &ui_hidden('cipher',$in{'cipher'});
print &ui_hidden('CLIENT_NAME',$in{'CLIENT_NAME'});
print &ui_hidden('dh','dh'.$$info_ca{'KEY_SIZE'}.'.pem');
print &ui_hidden('tls-auth',$tlsauth_server);
print &ui_hidden('modify',1);
print &ui_table_start($text{'modifyclient_server_title'}.' '.$in{'CLIENT_NAME'},'',2);
print &ui_table_row($text{'name'}, $in{'CLIENT_NAME'});
print &ui_table_row($text{'protocol'}, $in{'proto'},'width=100%');
print &ui_table_row($text{'dev'}, $in{'dev'});
print &ui_table_row($text{'ca'}, $$info_ca{'CA_NAME'},'width=100%');
print &ui_table_row($text{'choose_client'}, $text{'automatic_name'});
print &ui_table_row($text{'cert_client'}, $text{'automatic'});
print &ui_table_row($text{'key_client'}, $text{'automatic'});
print &ui_table_row($text{'dh'}, 'dh'.$$info_ca{'KEY_SIZE'}.'.pem','width=100%');
print &ui_table_row($text{'remote'}, $text{'remote_url'}.': '.&ui_textbox('remote_url',$in{'remote_url'},12).' '.$text{'remote_port'}.': '.$in{'remote_port'});

if ($tlsauth_server == $in{'tls-auth'}) {
    if ($in{'tls-auth'} == 1) {
	print &ui_table_row($text{'tls-auth'}, $text{'yes'}." ".$text{'automatic_server'});
    } else {
	print &ui_table_row($text{'tls-auth'}, $text{'no'}." ".$text{'automatic_server'});
    }
} else {
    if ($in{'tls-auth'} == 1) {
	print &ui_table_row($text{'tls-auth'}, "<span style=\"color:red\">".$text{'no'}." ".$text{'modified_server'}."</span>");
    } else {
	print &ui_table_row($text{'tls-auth'}, "<span style=\"color:red\">".$text{'yes'}." ".$text{'modified_server'}."</span>");
    }
}

if ($server_info{'cipher'} eq $in{'cipher'}) {
    print &ui_table_row($text{'cipher'}, $in{'cipher'}." ".$text{'automatic_server'});
} else {
    print &ui_table_row($text{'cipher'}, "<span style=\"color:red\">".$server_info{'cipher'}." ".$text{'modified_server'}."</span>");
}

print &ui_table_row($text{'comp-lzo'}, &ui_select('comp-lzo', $in{'comp-lzo'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'user'}, &ui_select('user', $in{'user'}, $a_user));
print &ui_table_row($text{'group'}, &ui_select('group', $in{'group'}, $a_group));
print &ui_table_row($text{'persist-key'}, &ui_select('persist-key', $in{'persist-key'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'persist-tun'}, &ui_select('persist-tun', $in{'persist-tun'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'keepalive'}, $text{'keepalive_ping'}.': '.&ui_textbox('keepalive_ping',$in{'keepalive_ping'},3)." ".$text{'keepalive_ping-restart'}.': '.&ui_textbox('keepalive_ping-restart',$in{'keepalive_ping-restart'},3));
print &ui_table_row($text{'verb'}, &ui_select('verb', $in{'verb'}, $a_verb));
print &ui_table_row($text{'mute'}, &ui_select('mute', $in{'mute'}, $a_mute));

if ($server_info{'tun-mtu'} == $in{'tun-mtu'}) {
    print &ui_table_row($text{'tun-mtu'}, $in{'tun-mtu'}." ".$text{'automatic_server'});
} else {
    print &ui_table_row($text{'tun-mtu'}, "<span style=\"color:red\">".$server_info{'tun-mtu'}." ".$text{'modified_server'}."</span>");
}

print &ui_table_row($text{'fragment'}, &ui_textbox('fragment',$in{'fragment'},4));

if ($server_info{'mssfix'} == $in{'mssfix'}) {
    print &ui_table_row($text{'mssfix'}, $in{'mssfix'}." ".$text{'automatic_server'});
} else {
    print &ui_table_row($text{'mssfix'}, "<span style=\"color:red\">".$server_info{'mssfix'}." ".$text{'modified_server'}."</span>");
}

print &ui_table_row($text{'float'}, &ui_select('float', $in{'float'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'auth-nocache'}, &ui_select('auth-nocache', $in{'auth-nocache'}, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
print &ui_table_row($text{'adds_conf'}, &ui_textarea('adds_conf', $in{'adds_conf'}, 5, 45, 'off'));
print &ui_table_end();
print &ui_table_start($text{'commands'},'',2);
print &ui_table_row($text{'up-pre'}, &ui_textarea('up-pre', $in{'up-pre'}, 3, 45, 'off'));
print &ui_table_row($text{'up'}, &ui_textarea('up', $in{'up'}, 3, 45, 'off'));
print &ui_table_row($text{'down-pre'}, &ui_textarea('down-pre', $in{'down-pre'}, 3, 45, 'off'));
print &ui_table_row($text{'down'}, &ui_textarea('down', $in{'down'}, 3, 45, 'off'));
print &ui_table_end();
print &ui_table_start($text{'ccdfile'},'',2);
print &ui_table_row($text{'ccdfile-content'}, &ui_textarea('ccdfile', $in{'ccdfile'}, 3, 45, 'off'));
print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

print "<BR><BR>";

#footer della pagina
&footer("clientlist_vpn.cgi?vpn=".$in{'vpn'}, $text{'list_client_vpn'}." ".$in{'vpn'});
