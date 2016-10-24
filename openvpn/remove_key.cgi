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

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

# chiave server
if (-f $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'}.'/'.$in{'ca_name'}.'/'.$in{'key_name'}.'.server') {
    ($listvpn,$list_static_vpn) = &ReadVPN();
    foreach $key (keys %{$listvpn}) {
	if ($$listvpn{$key}{VPN_ACTION} == 1 and $$listvpn{$key}{'key'} =~ /^$config{'openvpn_keys_subdir'}\/$$listvpn{$key}{'CA_NAME'}\/$in{'key_name'}\.key$/) {
	    #stoppo il server
	    $rv = &system_logged("$config{'stop_cmd'} $$listvpn{$key}{'VPN_NAME'} >/dev/null 2>&1 </dev/null");
	    if ($rv) { &error(&text('stop_fail', $config{'stop_cmd'}.' '.$$listvpn{$key}{'VPN_NAME'})); } 
	    else { print &text('stop_ok', $config{'stop_cmd'}.' '.$$listvpn{$key}{'VPN_NAME'}).'<BR>'; }
	}
    }
# chiave client
} else {
    opendir D,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'};
    @servers = readdir D;
    closedir D;
    foreach $vpn (@servers) {
	if (-d $config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$vpn and $vpn =~ /\w/) {
	    opendir D,$config{'openvpn_home'}.'/'.$config{'openvpn_clients_subdir'}.'/'.$vpn;
	    @clients = readdir D;
	    closedir D;
	    foreach $client (@clients) {
		if ($client eq $in{'key_name'}) {
		    #cancello il client
		    &remove_client($client,$vpn);
		}
	    }
	}
    }
}

&remove_key(\%in);

print "<table border width=100%>\n";
print "<tr bgcolor=red><td nowrap><b>".$in{'key_name'}.': '.$text{'key_removed'}."</b></td></tr>\n";
print "</table>\n";

print "<BR><BR>";

#footer della pagina
&footer("keyslist_ca.cgi?file_name=".$in{'ca_name'}, $text{'keyslistca'}.' '.$in{'ca_name'});
