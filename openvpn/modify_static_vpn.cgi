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

&ReadStaticVPNConf();

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

# form per nuova VPN
print &ui_form_start("create_static_vpn.cgi", "POST");	
print &ui_hidden('modify',1);
print &ui_hidden('management_url','127.0.0.1');
print &ui_hidden('VPN_NAME',$in{'vpn'});
print &ui_hidden('vpn_port',$in{'vpn_port'});
print &ui_table_start($text{'modifyvpn_static_title'});
# th row
print "<tr><td>\n";
print &ui_table_start();
print "<tr $tb>";
    print "<td valign=top><b>&nbsp;</b></td>\n";
    print "<td valign=top nowrap><b>".$text{'server'}."</b></td>\n";
    print "<td valign=top nowrap><b>".$text{'client'}."</b></td>\n";
print "</tr>\n";
print "<tr>";
    print "<td valign=top><b>".$text{'name'}."</b></td>\n";
    print "<td valign=top nowrap><b>".$in{'vpn'}."</b></td>\n";
    print "<td valign=top nowrap><b>&nbsp;</b></td>\n";
print "</tr>\n";
print "<tr>";
    print "<td valign=top><b>".$text{'port'}."</b></td>\n";
    print "<td valign=top nowrap><b>".$in{'vpn_port'}."</b></td>\n";
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
