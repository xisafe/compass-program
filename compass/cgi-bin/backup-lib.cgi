#!/usr/bin/perl
#
# Backup CGI for Endian Firewall
#
#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
#        |         Endi an GmbH/Srl                                                     |
#        |         Bergweg 41 Via Monte                                                |
#        |         39057 Eppan/Appiano                                                 |
#        |         ITALIEN/ITALIA                                                      |
#        |         info@endian.it                                                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        | http://www.fsf.org/                                                         |
#        +-----------------------------------------------------------------------------+
#


require '/var/efw/header.pl';
use File::Copy;
use File::Temp qw/ tempdir tempfile/;
use Sys::Hostname;

&validateUser();
$backupsets='/home/httpd/html/backup/';
$backup='/usr/local/bin/backup-create';
my $cmd_judgeCF='sudo /usr/local/bin/Judge_CF_Sata.sh';
$restore='/usr/local/bin/backup-restore';
#$factoryfile='/var/efw/factory/factory.tar.gz';
$factoryfile='/etc/efw/backup/factory.tar.gz';

$conffile    = "${swroot}/backup/settings";
$conffile_default = "${swroot}/backup/default/settings";

$errormessage = '';
%par;
%conf_hash;
$conf = \%conf_hash;

$gpgkey = '';
$gpgwrap = 'sudo /usr/local/bin/gpgwrap.sh';
%checked = ( 0 => '', 'on' => "checked='checked'" );

$createbackupusb = 'sudo /usr/local/bin/efw-backupusb --runbackup';
my $enabled_file = '/var/efw/time/enable';
my $mainsettings = '/var/efw/main/settings';
sub save_meta($$) {
    my $fname = shift;
    my $msg = shift;

    open(F, ">${fname}.meta") || return 1;
    print F "$msg";
    close(F);
}


sub loadconfig() {
    if (-e $conffile_default) {
        readhash($conffile_default, $conf);
    }
    if (-e $conffile) {
        readhash($conffile, $conf);
    }
    if ($conf->{'TIMEZONE'} =~ /^$/) {
        my %mainhash = ();
        my $mainconf = \%mainhash;
        readhash($mainsettings, $mainconf);
        $conf->{'TIMEZONE'} = $mainconf->{'TIMEZONE'};
        $conf->{'TIMEZONE'} =~ s+/usr/share/zoneinfo/(posix/)?++;
    }
    if (($conf->{'NTP_ADDR_1'} !~ /^$/) || ($conf->{'NTP_ADDR_2'} !~ /^$/)) {
        $conf->{'NTP_SERVER_LIST'} .= $conf->{'NTP_ADDR_1'}.",".$conf->{'NTP_ADDR_2'}.","
    }

    delete($conf->{'NTP_ADDR_1'});
    delete($conf->{'NTP_ADDR_2'});

    if (-e $enabled_file) {
        $enabled = 1;
    }
}

sub get_meta($) {
    my $fname = shift;
    open(F, "${fname}") || return "";
    my @msg = <F>;
    return join(" ",@msg);
}

sub format_date($) {
    my $number = shift;
    if ($number =~ /^(\d{4})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$/) {
        my $year=$1;
        my $month=$2;
        my $day=$3;
        my $hour=$4;
        my $minute=$5;
        my $second=$6;

        use DateTime;
        my $dt = DateTime->new(
           year   => $year,
           month  => $month,
           day    => $day,
           hour   => $hour,
           minute => $minute,
           second => $second
       );
       return $dt->strftime("%a, %d %b %Y %H:%M:%S");
    }
    return $number;
}

sub get_now() {
	loadconfig();
    use DateTime;
    my $dt = DateTime->now(time_zone=>$conf->{'TIMEZONE'});
    return $dt->strftime("%Y%m%d%H%M%S");
}

sub check_archive($) {
    my $arch = shift;
    use File::Path;

    my $content='';
    if (! -e $arch) {
        return (1,'');
    }
    my $tmp = tempdir('importXXXXXX', DIR=> '/tmp/');
    return '' if ($tmp !~ /^\/tmp/);
####################################################33
    my $arch_gpg = $arch.".gpg";
    system("mv $arch $arch.gpg"); 
    system("echo gpg --homedir /root/.gnupg --always-trust --batch --decrypt --recipient 5E044767 -o $arch $arch_gpg >/tmp/mawen-gpg"); 
    if (system("sudo gpg --homedir /root/.gnupg --always-trust --batch --decrypt --recipient 5E044767 -o $arch $arch_gpg &>/tmp/testgpg") != 0) {
        system("echo decrypt_error >/tmp/mawen-test-gpg");
        rmtree($tmp);
        #return '';
    }
    else
        {system("echo decrypt_ok >/tmp/mawen-test-gpg");}
####################################################33

    if (system("tar -C $tmp -xzf $arch &>/dev/null") != 0) {
        rmtree($tmp);
        return '';
    }
    if (-e "$tmp/var/efw/dhcp/") {
        $content.='-settings';
    }
    if (-e "$tmp/var/efw/pgsql/psql-latest.dump.bz2" || -e "$tmp/var/efw/mysql/mysql-latest.dump.bz2") {
        $content.='-db';
    }
    if (-e "$tmp/var/log/messages") {
        $content.='-logs';
    }
##bug213-ÉÏ´«µÄ±¸·ÝÎÄ¼þ²»ÄÜÊ¶±ð´æÔÚlogarchieve(Ñ¹Ëõµµ°¸)
    #if (-e "$tmp/var/log/messages.*.gz") {
    #    $content.='-logarchive';
    #}
	my @messages_files = glob "$tmp/var/log/messages*.gz";
	if(scalar(@messages_files) ne 0)
	{
		$content.='-logarchive';
	}
##bug213-Cynthia
    rmtree($tmp);
    return $content;
}

sub import_archive() {
    if (ref ($par{'IMPORT_FILE'}) ne 'Fh')  {
	$errormessage = _('No data was uploaded');
        return 0;
    }
    my ($fh, $tmpfile) = tempfile("import.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.tar.gz');
    if (!copy ($par{'IMPORT_FILE'}, $fh)) {
	$errormessage = _('Unable to save configuration archive file %s: \'%s\'', $par{'IMPORT_FILE'}, $!);
	return 0;
    }
    close($fh);

    my $now=get_now();
	
    my $hostname=hostname();

    my $content = check_archive($tmpfile);
    if ($content =~ /^$/) {
        unlink($tmpfile);
        $errormessage = _('Invalid backup archive!');
        return 0;
    }

    my $newfilename1 = "$backupsets/backup-${now}-${hostname}${content}.tar.gz";
    my $newfilename = "$backupsets/backup-${now}-${hostname}${content}.tar.gz.gpg";
    system("echo $tmpfile $newfilename >/tmp/movefile");

    system("sudo /usr/local/bin/chown.sh");
    if (! move($tmpfile.".gpg", $newfilename)) {
        unlink($tmpfile);
        $errormessage = _('Could not bring imported backup archive in place! (%s)', $!);
        return 0;
    }

    if (save_meta($newfilename1, $par{'REMARK'}))
	{system("echo 123>/tmp/testmeta");}

    system("sudo /usr/local/bin/chown.sh");
    system("echo $tmpfile $newfilename1 >/tmp/movefile");
    if (! move($tmpfile, $newfilename1)) {
        unlink($tmpfile);
        $errormessage = _('Could not create the decryption backup archive in place! (%s)', $!);
        return 0;
    }
    $notemessage = _('Backup archive successfully imported.');
    return 1;
}

sub factory() {
    if (! -x "/usr/local/bin/factory-default") {
        $errormessage = _('Could not bring the machine to factory defaults!');
        return 0;
    }
    system("/usr/local/bin/factory-default &");
    return 1;
}

sub remove_archive($) {
    my $basename = shift;
    #pj:2016-09-21  add a limit to remove special name
    # if ($basename =~ /^$/ || $basename =~ /[\*\?\[\]\(\){}<>\/"';]/) {
    #    return 0;
    # }
    # my @arr = split("-",$basename);
    # if($arr[1] !~ /^[0-9]+$/){
    #     return 0;
    # }
    # pj ：end
    
    if ( -e "$backupsets/$basename") {
        unlink("$backupsets/$basename");
    }
    if ( -e "$backupsets/$basename.meta") {
        unlink("$backupsets/$basename.meta");
    }
    if ( -e "$backupsets/$basename.gpg") {
        unlink("$backupsets/$basename.gpg");
    }
    if ( -e "$backupsets/$basename.dat") {
        unlink("$backupsets/$basename.dat");
    }
    if ( -e "$backupsets/$basename.mailerror") {
        unlink("$backupsets/$basename.mailerror");
    }
    if ( -e "$backupsets/$basename.gpg.mailerror") {
        unlink("$backupsets/$basename.gpg.mailerror");
    }
    if (-e "$backupsets/$basename") {
        $errormessage = _('Backup archive "%s" not removed!', $basename);
        return 0;
    }
    $notemessage = _('Backup archive "%s" successfully removed!', $basename);
    return 1;
}

sub call($) {
    my $cmd = shift;
    use IPC::Open3;

    $pid = open3(\*WRITE, \*READ, \*ERROR, $cmd);
    if (! $pid) {
        return (0, _('Could  not call "%s"', $cmd));
    }
    close WRITE;
    my @err = <ERROR>;
    my @out = <READ>;
    close READ;
    close WRITE;

    my $reterr = join(" ", @err);
    my $retout = join(" ", @out);

    my $ret = 0;
    waitpid($pid, 0);
    if ($? == 0) {
        $ret = 1;
    }
    return ($ret, $reterr, $retout);
}

sub create($$$$$$$) {
    my $settings=shift;
    my $rules=shift;
    my $dbdumps=shift;
    my $logs=shift;
    my $logarchives=shift;
    my $remark=shift;
    my $vm=shift;
    my $backupcmd="$backup";
    
    system("$cmd_judgeCF");
    if($? >> 8 == 5){
        $errormessage = "nospace";
        return 1;
    }

    if ($settings) {
       $backupcmd.=" --settings";
    }
    if ($rules) {
       $backupcmd.=" --rules";
    }
    if ($dbdumps) {
       $backupcmd.=" --dbdumps";
    }
    # if ($logs) {
       # $backupcmd.=" --logs" 
    # }
    # if ($logarchives) {
       # $backupcmd.=" --logarchives" 
    # }
	if ($vm) {
		$backupcmd.=" --virtualmachines";
	}
    if ($remark !~ /^$/) {
       $backupcmd.=" --message=\"$remark\"";
    }
    if (($conf->{'BACKUP_ENCRYPT'} eq 'on') && ($conf->{'BACKUP_GPGKEY'} !~ /^$/)) {
       $backupcmd.=" --gpgkey=$conf->{'BACKUP_GPGKEY'}";
    }
    #if (! $settings && ! $logs && ! $dbdumps && ! $logarchives && ! $vm) {
    if (! $settings && ! $rules && ! $vm) {
        $errormessage = _('Include at least something to backup!');
        return 0;
    }
    my ($r, $e, $o) = call($backupcmd);

    if (! $r) {
        $errormessage = _('Could not create new backup because "%s".', $e);
        return 0;
    }

    if (-e $o) {
        $errormessage = _('Backup not created!');
        return 0;
    }
    $notemessage = _('Backup successfully created.');
    return 1;
}

sub restore($) {
    my $basename = shift;
    my $backupcmd="$restore --reboot $backupsets/$basename";

    if (! -e "$backupsets/$basename") {
    	if (! -e "$backupsets/$basename.dat") {
	
	        $errormessage = _('Backup set "%s" not found!', $basename);
        	return 0;
	}
	
    	$backupcmd="$restore --decrypt --gpgfile $backupsets/$basename.dat --reboot $backupsets/$basename";
    }
    if ($basename =~ /.gpg$/) {
        $errormessage = _('Cannot restore encrypted backups!');
        return 0;
    }
    system($backupcmd);
    if($? >> 8 == 5){
        $errormessage = "nospaceforCF";
        return 0;
    }
    return 1;    
}

sub display_reboot() {
    my $title='';
    if ($par{'ACTION'} eq 'restore') {
        $title = _('Restore is in progress! Please wait until reboot!');
    }
    if ($par{'ACTION'} eq 'factory') {
        $title = _('Reset to factory default is in progress! Please wait until reboot!');
    }
    openbox('100%', 'left', $title);
    printf <<END
<br />
<br />
<div align='center'>
  <img src='/images/reboot_splash.png' />
<br /><br />
<font size='6'>$title</font>
</div>
END
;

    closebox();
}

sub save() {
    if ($gpgkey !~ /^$/) {
        chomp($gpgkey);
        $conf->{'BACKUP_GPGKEY'} = $gpgkey;
    }
    $conf->{'BACKUP_ENCRYPT'} = $par{'BACKUP_ENCRYPT'};
    &writehash("${swroot}/backup/settings", $conf);
}

sub configure_gpgkey() {
    save();

    if (ref ($par{'IMPORT_FILE'}) ne 'Fh')  {
        return 1;
    }

    my ($fh, $tmpfile) = tempfile("gpgkey.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.tar.gz');
    if (!copy ($par{'IMPORT_FILE'}, $fh)) {
        $errormessage = _('Unable to store GPG public key: \'%s\'', $par{'IMPORT_FILE'}, $!);
        return 0;
    }
    close($fh);
    my ($r, $e, $o) = call("$gpgwrap --import ".$tmpfile);

    if (! $r) {
        $errormessage = _('Could not import GPG public key because "%s".', $e);
        return 0;
    }

    if ($o =~ /^$/) {
        my $err = _('No GPG user ID found');
        $errormessage = _('Could not import GPG public key because "%s".', $err);
        return 0;
    }
    unlink($tmpfile);
    $gpgkey = $o;
    $notemessage = _('GPG public key "%s" imported successfully', $gpgkey);
    save();
    return 1;
}

sub doaction() {
    return factory() if ($par{'ACTION'} eq 'factory');
    return restore($par{'ARCHIVE'}) if ($par{'ACTION'} eq 'restore');
    if (($par{'ACTION'} eq 'create') and ( $par{'CREATEBACKUPUSB'})) {
        if ($par{'REMARK'}) {
            system($createbackupusb . " --message \"$par{'REMARK'}\" &>/dev/null &");
        } else {
            system($createbackupusb . " &>/dev/null &");
	}
    } elsif ($par{'ACTION'} eq 'create') {
        create($par{'SETTINGS'}, $par{'RULES'}, $par{'DBDUMPS'}, $par{'LOGS'}, $par{'LOGARCHIVES'}, $par{'REMARK'}, $par{'VIRTUALMACHINES'});
    }
    remove_archive($par{'ARCHIVE'}) if ($par{'ACTION'} eq 'remove');
    import_archive() if ($par{'ACTION'} eq 'import');
    configure_gpgkey() if ($par{'ACTION'} eq 'gpgkey');
    
    return 0;
}


