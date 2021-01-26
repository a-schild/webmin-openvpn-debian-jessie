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

&ReadFieldsCA($in{'ca'});

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
#$a_cypher = [];
#&open_execute_command(CMD, $config{'openvpn_path'} . ' --show-ciphers', 2);
#while ($row=<CMD>) {
#    $row =~ s/\r*\n//g;
#    if (($row =~ /bit default key/i) or ($row =~ /bit key,/i) or ($row =~ /bit key by default,/i)) {
#	($key) = split(' ',$row);
#	push(@$a_cypher,[$key,$row]);	
#    }
#}
#close(CMD);

#array of aviable ethernet devices
$a_eth = &ReadEths($in{'devbr'});
#$a_eth = [];
#&open_execute_command(CMD, 'ifconfig|grep -i :ethernet |awk \'{print $1}\'', 2);
#while ($row=<CMD>) {
#	$row =~ s/\r*\n//g;
#	if (($row ne $in{'devbr'}) && (($row !~ /^tap\d/))) {
#		push(@$a_eth,[$row,$row]);
#	}
#}
#close(CMD);

# estrarre elenco chiavi server [della ca selezionata]
$a_server = &ReadCAKeys($in{'ca'},2,1);

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";

if (@$a_server) {
    # form per nuova VPN
    print &ui_form_start("create_vpn.cgi", "POST");
    print &ui_hidden('ca_dir',$config{'openvpn_keys_subdir'}.'/'.$in{'ca'});
    print &ui_hidden('ca',$config{'openvpn_keys_subdir'}.'/'.$in{'ca'}.'/ca.crt');
    print &ui_hidden('ca_name',$in{'ca'});
    print &ui_hidden('ccd-exclusive',1);
    print &ui_hidden('management_url','127.0.0.1');
    print &ui_hidden('dh',$config{'openvpn_keys_subdir'}.'/'.$in{'ca'}.'/dh'.$$info_ca{'KEY_SIZE'}.'.pem');
    print &ui_hidden('crl-verify',$config{'openvpn_keys_subdir'}.'/'.$in{'ca'}.'/crl.pem');
    print &ui_table_start($text{'newvpn_server_title'},'',2);
    print &ui_table_row($text{'name'}, &ui_textbox('VPN_NAME','changeme',50));
    print &ui_table_row($text{'port'}, &ui_textbox('port','1194',50));
    print &ui_table_row($text{'protocol'}, &ui_select('proto', 'udp', [ ['udp','udp'],['tcp-server','tcp-server'],['tcp-client','tcp-client'] ]));
    print &ui_table_row($text{'dev'}, &ui_select('dev', 'tun', [ ['tun','tun'],['tap','tap'] ]));
##############################
##############################
    print bridge_control_elements();
##############################
##############################
    print &ui_table_row($text{'management'}, $text{'management_enable'}.': '.&ui_select('management', '0', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]).' '.$text{'management_url'}.': 127.0.0.1 '.$text{'management_port'}.': '.&ui_textbox('management_port','',5));
    print &ui_table_row($text{'ca'}, $in{'ca'});
    print &ui_table_row($text{'choose_server'}, &ui_select('choose_server', '', $a_server));
    print &ui_table_row($text{'cert_server'}, $text{'automatic'});
    print &ui_table_row($text{'key_server'}, $text{'automatic'});
    print &ui_table_row($text{'dh'}, 'dh'.$$info_ca{'KEY_SIZE'}.'.pem');
    print &ui_table_row($text{'tls-server'}, &ui_select('tls-server', '0', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'local'}, &ui_textbox('local','ALL',50));
    print &ui_table_row($text{'new_vpn_server'}, $text{'network'}.''.&ui_textbox('network','',15)." ".$text{'netmask'}.''.&ui_textbox('netmask','',15));
    print &ui_table_row($text{'ifconfig-pool-persist'}, &ui_select('ifconfig-pool-persist', '0', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'client-to-client'}, &ui_select('client-to-client', '0', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'duplicate-cn'}, &ui_select('duplicate-cn', '0', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'tls-auth'}, &ui_select('tls-auth', '0', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'ccd-exclusive'}, $text{'yes'});
    print &ui_table_row($text{'cipher'}, &ui_select('cipher', '0', $a_cypher));
    print &ui_table_row($text{'comp-lzo'}, &ui_select('comp-lzo', '1', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'max-clients'}, &ui_textbox('max-clients','100',4));
    print &ui_table_row($text{'user'}, &ui_select('user', 'nobody', $a_user));
    print &ui_table_row($text{'group'}, &ui_select('group', 'nogroup', $a_group));
    print &ui_table_row($text{'persist-key'}, &ui_select('persist-key', '1', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'persist-tun'}, &ui_select('persist-tun', '1', [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'keepalive'}, $text{'keepalive_ping'}.': '.&ui_textbox('keepalive_ping','10',3)." ".$text{'keepalive_ping-restart'}.': '.&ui_textbox('keepalive_ping-restart','120',3));
    print &ui_table_row($text{'verb'}, &ui_select('verb', '2', $a_verb));
    print &ui_table_row($text{'mute'}, &ui_select('mute', '20', $a_mute));
    print &ui_table_row($text{'status'}, 'openvpn-status.log');
    print &ui_table_row($text{'log-append'}, 'openvpn.log');
    print &ui_table_row($text{'tun-mtu'}, &ui_textbox('tun-mtu','',4));
    print &ui_table_row($text{'fragment'}, &ui_textbox('fragment','',4));
    print &ui_table_row($text{'mssfix'}, &ui_textbox('mssfix','',4));
    print &ui_table_row($text{'float'}, &ui_select('float', 0, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'chroot'}.' '.$config{'openvpn_home'}, &ui_select('chroot', 0, [ ['0',$text{'no'}],['1',$text{'yes'} ] ]));
    print &ui_table_row($text{'topology'}, &ui_select('topology',0, [ ['subnet','subnet'],['net30','net30'],['p2p','p2p'] ]));
    print &ui_table_row($text{'adds_conf'}, &ui_textarea('adds_conf', '', 5, 45, 'off'));
    print &ui_table_end();
    print &ui_table_start($text{'commands'},'',2);
    print &ui_table_row($text{'up-pre'}, &ui_textarea('up-pre', '', 3, 45, 'off'));
    print &ui_table_row($text{'up'}, &ui_textarea('up', '', 3, 45, 'off'));
    print &ui_table_row($text{'down-pre'}, &ui_textarea('down-pre', '', 3, 45, 'off'));
    print &ui_table_row($text{'down'}, &ui_textarea('down', '', 3, 45, 'off'));
    print &ui_table_row($text{'down-root'}, &ui_textarea('down-root', '', 3, 45, 'off'));
    print &ui_table_end();
    print &ui_form_end([ [ "save", $text{'save'} ] ]);
} else {
    # start tabella
    print "<table border width=100%>\n";
    # title row
    print "<tr $tb>";
	print "<td nowrap><b>".$text{'list_keys_server_empty'}."</b></td>\n";
    print "</tr>\n";
    print "</table>\n";
}
print "<BR><BR>";

#footer della pagina
&footer("listvpn.cgi", $text{'listserver_title'});
