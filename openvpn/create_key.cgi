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

# Controlli parametri form
$in{'KEY_NAME'} = lc($in{'KEY_NAME'});
if (($in{'KEY_NAME'} !~ /^[a-zA-Z0-9_\-\.]{4,}$/) or ($in{'KEY_NAME'} =~ /\.{2,}/) or ($in{'KEY_NAME'} =~ /\.$/)){
    &error($text{'error_key_name_1'}.": $&");
}

if ($in{'KEY_PASSWD'} and $in{'KEY_PASSWD'} !~ /\w{4}/ and $in{'KEY_SERVER'} != 1) {
    &error($text{'error_key_password'});
}

if ($in{'KEY_PKCS12'} == 2 and ($in{'KEY_PKCS12_PASSWD'} !~ /\w{4}/ or !$in{'KEY_PASSWD'})) {
    &error($text{'error_key_pkcs12_password'});
}

if ($in{'KEY_EXPIRE'} =~ /\D/) {
    &error($text{'error_key_expire'});
}

if ($in{'KEY_COUNTRY'} !~ /\S/) {
    &error($text{'error_key_country'});
}

if ($in{'KEY_PROVINCE'} !~ /\S/) {
    &error($text{'error_key_province'});
}

if ($in{'KEY_CITY'} !~ /\S/) {
    &error($text{'error_key_city'});
}

if ($in{'KEY_ORG'} !~ /\S/) {
    &error($text{'error_key_org'});
}

if ($in{'KEY_EMAIL'} !~ /\S/) {
    &error($text{'error_key_email_1'});
} elsif ($in{'KEY_EMAIL'} !~ /^\S+@\S+$/) {
    &error($text{'error_key_email_2'});
}

$in{'KEY_CN'} = $in{'KEY_NAME'};

if (-s $in{'KEY_DIR'}.'/'.$in{'KEY_NAME'}.".key" or -s $in{'KEY_DIR'}.'/'.$in{'KEY_NAME'}.".csr") { &error($text{'error_key_name_2'}); }

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

&create_key(\%in);

if ($in{'KEY_SERVER'} == 1) {
    open S,">".$in{'KEY_DIR'}."/".$in{'KEY_NAME'}.".server";
    print S "Do not remove this file. It will be used from webmin OpenVPN Administration interface.";
    close S;
}

print "<BR><BR>";

#footer della pagina
&footer("keyslist_ca.cgi?file_name=".$in{'ca_name'}, $text{'list_keys_of_ca'}." ".$in{'ca_name'});
