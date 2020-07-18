from app import app, db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, StaffRegistrationForm, AdminRegistrationForm, EditStaffInfoForm, PrcessedSamplesForm, RegisterStationsForm, RegisterShiftForm, FilterPlateDateForm, RetestFileForm, RunSummaryFileForm
from app.models import User, Member, ProcessedSamples, Station, Shift, AssignedMemberToStations, AssignedMemberToShift, Retests, RunSummary, RunSummary1
import os
from datetime import date, datetime, timedelta
from sqlalchemy.sql import func
import random
import psycopg2
import xlrd
from pandas import read_csv, concat
'''import pandas as pd
import numpy as np
from pandas import read_csv
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC'''


@app.route('/')
@app.route('/index')
def index():
	#processed samples
	#run_dates = ProcessedSamples.query.distinct(ProcessedSamples.process_date).order_by(ProcessedSamples.process_date.asc()).all()#having errors in group_by
	run_dates = ProcessedSamples.query.group_by(ProcessedSamples.process_date).order_by(ProcessedSamples.process_date.asc()).all()
	processed_samples = ProcessedSamples.query.order_by(ProcessedSamples.process_date.asc()).all()
	runs_list = []
	for r in run_dates:
		r.day = r.process_date.strftime('%A')
		r.run = {'run_date': str(r.process_date) + ' - ' + r.day }
		runs_list.append(r.run)
		for p in processed_samples:
			if r.process_date == p.process_date:
				if p.shift.name == 'Morning':
					r.run['Morning'] = p.quantity
				if p.shift.name == 'Afternoon':
					r.run['Afternoon'] = p.quantity
				if p.shift.name == 'Night':
					r.run['Night'] = p.quantity
					
	#distribute members to each tier i.e based on length of emplyment
	shifts = Shift.query.all()
	members = Member.query.order_by(Member.date_joined.asc()).all()
	# print([(member.name, member.days_employed()) for member in members])
	shift_member_len = 0
	if len(shifts) != 0 and len(members) != 0:
		shift_member_len = len(members)//len(shifts)
	
	i = 0
	tiers = []
	for x in range(0, len(shifts)):
		member_tier = []
		if x < (len(shifts) - 1):
			member_tier.append(members[i:i+shift_member_len])
			i = i+shift_member_len
		else:
			member_tier.append(members[i:])
		tiers.append(*member_tier)
	
	#distribute members per tier to each shift
	morning_shift = []
	noon_shift = []
	night_shift = []

	shift_staff_len = 1
	try:
		if shift_member_len//len(tiers) > 1:
			shift_staff_len = shift_member_len//len(tiers)
	except ZeroDivisionError:
		pass
	# morning shift
	for tier in tiers:
		shift_staff = random.sample(tier, shift_staff_len)
		'''for r_staff in shift_staff:
			r_staff_index = tier.index(r_staff)
			tier.pop(r_staff_index)'''
		
		morning_shift.append(shift_staff)
	
	morning_shift = [staff for sublist in morning_shift for staff in sublist]
	
	# noon shift
	for tier in tiers:
		for r_staff in morning_shift:
			try:
				r_staff_index = tier.index(r_staff)
				tier.pop(r_staff_index)
			except ValueError:
				pass
		
		shift_staff = random.sample(tier, shift_staff_len)

		noon_shift.append(shift_staff)
	noon_shift = [staff for sublist in noon_shift for staff in sublist]

	# night shift
	for tier in tiers:
		for r_staff in morning_shift:
			try:
				r_staff_index = tier.index(r_staff)
				tier.pop(r_staff_index)
			except ValueError:
				pass

		for r_staff in noon_shift:
			try:
				r_staff_index = tier.index(r_staff)
				tier.pop(r_staff_index)
			except ValueError:
				pass
		if len(tier) < shift_staff_len:
			shift_staff = random.sample(tier, len(tier))
		else:
			shift_staff = random.sample(tier, shift_staff_len)
		
		night_shift.append(shift_staff)
	night_shift = [staff for sublist in night_shift for staff in sublist]

	

	'''distributed_tiers = []
	j = 0
	for x in range(shift_member_len):
		distributed_tiers.append([member[j] for member in tiers] )
		j += 1

	morning_shift = []
	noon_shift = []
	night_shift = []
	for x in distributed_tiers:
		k = 0
		morning_shift.append(distributed_tiers[k])
		distributed_tiers.pop(k)
		k += 1
		noon_shift.append(distributed_tiers[k])
		distributed_tiers.pop(k)
		k += 1
		night_shift.append(distributed_tiers[k])
		distributed_tiers.pop(k)'''
		
	'''print('morning', morning_shift)
	print('noom', noon_shift)
	print('night', night_shift)'''
		#distributed_members
	#for member in members:
	#    print(member.name, member.days_employed())

	#assign member to stations
	stations = Station.query.all()
	for station in stations:
		for member in members:
			pass

	return render_template('index.html', title='Home', runs_list=runs_list, members=members, morning_shift=morning_shift, noon_shift=noon_shift, night_shift=night_shift)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    admin_reg_form = AdminRegistrationForm()
    if admin_reg_form.validate_on_submit():
        user_q = User.query.filter_by(name=admin_reg_form.name.data).first()
        if user_q is None:
            user = User(name=admin_reg_form.name.data, date_joined=admin_reg_form.date_joined.data)
            user.set_password(admin_reg_form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Thank you for registering, you will be notified once registration is approved.')
            return redirect(url_for('admin_login'))
        else:
            flash('Name already registered.')
            return redirect(url_for('register'))
    return render_template('register.html', title='Register', admin_reg_form=admin_reg_form)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
	if current_user.is_authenticated:
		return redirect(url_for('admin'))
		
	login_form = LoginForm()
	if login_form.validate_on_submit():
		user = User.query.filter_by(name=login_form.name.data, verified=True).first()
		unverified_user = User.query.filter_by(name=login_form.name.data, verified=False).first()
		if unverified_user:
			flash('Registration not yet verified.')
			return redirect(url_for('index'))
		if user is None or not user.check_password(login_form.password.data):
			flash('Name not registered or invalid password')
			return redirect(url_for('admin_login'))
		login_user(user, remember=login_form.remember_me.data)
		return redirect(url_for('admin'))
	return render_template('admin_login.html', title='Admin', login_form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    admins = User.query.filter_by(verified=True).all()
    admin_requests = User.query.filter_by(verified=False).all()
    members = Member.query.all()
    staff_reg_form = StaffRegistrationForm()
    if staff_reg_form.submit.data and staff_reg_form.validate_on_submit():
        member_q = Member.query.filter_by(name=staff_reg_form.name.data).first()
        if member_q is None:
            member = Member(name=staff_reg_form.name.data, date_joined=staff_reg_form.date_joined.data, position=staff_reg_form.position.data)
            db.session.add(member)
            db.session.commit()
            flash(member.name + ' registered as team member.')
            return redirect(url_for('admin'))
        else:
            flash('Member name already registered.')
            return redirect(url_for('admin'))
    esi_form = EditStaffInfoForm()
    shifts = Shift.query.all()
    shift_list = [(s.id, s.name) for s in shifts]
    ps_form = PrcessedSamplesForm()
    ps_form.shift.choices = shift_list
    if ps_form.submit.data and ps_form.validate_on_submit():
        sample_q = ProcessedSamples.query.filter_by(process_date=ps_form.date.data, shift_id=ps_form.shift.data).first()
        if sample_q is None:
            samples = ProcessedSamples(process_date=ps_form.date.data, shift_id=ps_form.shift.data, quantity=ps_form.quantity.data)
            db.session.add(samples)
            db.session.commit()
            flash('Processed samples for ' + str(samples.process_date) + ' - ' + samples.shift.name + ' shift has been saved.')
            return redirect(url_for('admin'))
        else:
            flash('An existing data has already been saved for ' + str(sample_q.process_date) + ' - ' + sample_q.shift.name + ' shift.')
            return redirect(url_for('admin'))
    processed_samples = ProcessedSamples.query.all()

    rs_form = RegisterStationsForm()
    if rs_form.submit.data and rs_form.validate_on_submit():
        station = Station(name=rs_form.name.data, asignments=rs_form.assignments.data)
        db.session.add(station)
        db.session.commit()
        flash('Station ' + station.name + ' saved.')
        return redirect(url_for('admin'))
    rsh_form = RegisterShiftForm()
    if rsh_form.submit.data and rsh_form.validate_on_submit():
        shift = Shift(name=rsh_form.name.data)
        db.session.add(shift)
        db.session.commit()
        flash('Shift ' + shift.name + ' successfully registered.')
        return redirect(url_for('admin'))
    return render_template('admin.html', title='Admin', staff_reg_form=staff_reg_form, admins=admins, admin_requests=admin_requests, members=members, esi_form=esi_form, ps_form=ps_form, processed_samples=processed_samples, rs_form=rs_form, rsh_form=rsh_form)


@app.route('/data_uploads', methods=['GET', 'POST'])
def data_uploads():
	form = RetestFileForm()
	if form.validate_on_submit():
		#filename = secure_filename(form.fileContents.data.filename)  
		filestream =  form.retest_file_name.data 
		filestream.seek(0)#read file without saving
		names = ['sample_id', 'plate_id', 'well', 'fam', 'vic', 'analyst', 'retest_type', 'reason', 'remarks', 'admin_comment']
		dataset = concat((chunk for chunk in read_csv(filestream, names=names, chunksize=10000, keep_default_na=False)))#read_csv(file_loc, chunksize=1000, sep='\n')
		for i in range(1, len(dataset)):
			try:
				if dataset.loc[i, 'sample_id'] and dataset.loc[i, 'plate_id'] != '' or '\\':
					retest_query = Retests.query.filter_by(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well']).first()
					if not retest_query:
						if dataset.loc[i, 'sample_id'] and dataset.loc[i, 'plate_id'] and dataset.loc[i, 'well'] != '':
							if dataset.loc[i, 'fam'] != '' and dataset.loc[i, 'vic'] != '':
								retests_data = Retests(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well'], fam=dataset.loc[i, 'fam'], vic=dataset.loc[i, 'vic'], analyst=dataset.loc[i, 'analyst'], retest_type=dataset.loc[i, 'retest_type'], reason=dataset.loc[i, 'reason'], remarks=dataset.loc[i, 'remarks'], admin_comment=dataset.loc[i, 'admin_comment'])
								db.session.add(retests_data)
								#db.session.commit()
							elif dataset.loc[i, 'fam'] == '' and dataset.loc[i, 'vic'] != '':
								retests_data = Retests(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well'], vic=dataset.loc[i, 'vic'], analyst=dataset.loc[i, 'analyst'], retest_type=dataset.loc[i, 'retest_type'], reason=dataset.loc[i, 'reason'], remarks=dataset.loc[i, 'remarks'], admin_comment=dataset.loc[i, 'admin_comment'])
								db.session.add(retests_data)
								#db.session.commit()
							elif dataset.loc[i, 'vic'] == '' and dataset.loc[i, 'fam'] != '':
								retests_data = Retests(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well'], fam=dataset.loc[i, 'fam'], analyst=dataset.loc[i, 'analyst'], retest_type=dataset.loc[i, 'retest_type'], reason=dataset.loc[i, 'reason'], remarks=dataset.loc[i, 'remarks'], admin_comment=dataset.loc[i, 'admin_comment'])
								db.session.add(retests_data)
								#db.session.commit()
							elif dataset.loc[i, 'fam'] == '' and dataset.loc[i, 'vic'] == '':
								retests_data = Retests(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well'], analyst=dataset.loc[i, 'analyst'], retest_type=dataset.loc[i, 'retest_type'], reason=dataset.loc[i, 'reason'], remarks=dataset.loc[i, 'remarks'], admin_comment=dataset.loc[i, 'admin_comment'])
								db.session.add(retests_data)
								#db.session.commit()
							db.session.commit()
			except KeyError:
				pass
				
	form2 = RunSummaryFileForm()
	if form2.validate_on_submit():
		filestream2 =  form2.run_summary_file_name.data 
		filestream2.seek(0)#read file without saving
		names2 = ['plate_id', 'shift', 'date', 'blank_lot', 'pc_lot', 'extraction_operator', 'dispensing_start', 'dispensing_end', 'sample_qty', 'extraction_rgt_lot', 'mlb_load_time', 'machine_id', 'plate_load_time', 'qpcr_mix_lot', 'mgisp_tips_lot', 'machine_operator', 'dispensing', 'verifier']
		dataset2 = concat((chunk for chunk in read_csv(filestream2, names=names2, chunksize=10000, keep_default_na=False)))
		for i in range(1, len(dataset2)):
			try:
				if dataset2.loc[i, 'extraction_operator'] != '':
					extraction_operator_ = dataset2.loc[i, 'extraction_operator'].replace(' ', '/')
					extraction_operator = extraction_operator_.split('/')
					dataset2.loc[i, 'dispensing'] = extraction_operator[0]
					try:
						dataset2.loc[i, 'verifier'] = extraction_operator[1]
					except IndexError:
						pass
				
				if dataset2.loc[i, 'dispensing_start'] != '':	
					dispensing_start_ = dataset2.loc[i, 'dispensing_start'].replace('A', '').replace('a', '').replace('P', '').replace('p', '').replace('M', '').replace('m', '').replace(' ', '')
					try:
						dispensing_start = datetime.strptime(dispensing_start_, '%I:%M')
						dataset2.loc[i, 'dispensing_start'] = dispensing_start.time()
					except ValueError:
						dataset2.loc[i, 'dispensing_start'] = ''
						
				if dataset2.loc[i, 'dispensing_end'] != '':	
					dispensing_end_ = dataset2.loc[i, 'dispensing_end'].replace('A', '').replace('a', '').replace('P', '').replace('p', '').replace('M', '').replace('m', '').replace(' ', '')
					try:
						dispensing_end = datetime.strptime(dispensing_end_, '%I:%M')
						dataset2.loc[i, 'dispensing_end'] = dispensing_end.time()
					except ValueError:
						dataset2.loc[i, 'dispensing_end'] = ''		
						
				if dataset2.loc[i, 'plate_load_time'] != '':	
					plate_load_time_ = dataset2.loc[i, 'plate_load_time'].replace('A', '').replace('a', '').replace('P', '').replace('p', '').replace('M', '').replace('m', '').replace(' ', '')
					try:
						plate_load_time = datetime.strptime(plate_load_time_, '%I:%M')
						dataset2.loc[i, 'plate_load_time'] = plate_load_time.time()
					except ValueError:
						dataset2.loc[i, 'plate_load_time'] = ''		
				
				if dataset2.loc[i, 'mlb_load_time'] != '':	
					mlb_load_time_ = dataset2.loc[i, 'mlb_load_time'].replace('A', '').replace('a', '').replace('P', '').replace('p', '').replace('M', '').replace('m', '').replace(' ', '')
					try:
						mlb_load_time = datetime.strptime(mlb_load_time_, '%I:%M')
						dataset2.loc[i, 'mlb_load_time'] = mlb_load_time.time()
					except ValueError:
						dataset2.loc[i, 'mlb_load_time'] = ''
				
				run_summary_query = RunSummary1.query.filter_by(plate_id=dataset2.loc[i, 'plate_id'], shift=dataset2.loc[i, 'shift'], dispensing_start=dataset2.loc[i, 'dispensing_start'], plate_load_time=dataset2.loc[i, 'plate_load_time']).first()
				if not run_summary_query:
					try:
						run_summary = RunSummary1(plate_id=dataset2.loc[i, 'plate_id'], shift=dataset2.loc[i, 'shift'], blank_lot=dataset2.loc[i, 'blank_lot'], pc_lot=dataset2.loc[i, 'pc_lot'], sample_dispensing=dataset2.loc[i, 'dispensing'], verifier=dataset2.loc[i, 'verifier'], dispensing_start=dataset2.loc[i, 'dispensing_start'], dispensing_finish=dataset2.loc[i, 'dispensing_end'], sample_qty=dataset2.loc[i, 'sample_qty'], extraction_rgt_lot=dataset2.loc[i, 'extraction_rgt_lot'], machine_id=dataset2.loc[i, 'machine_id'], plate_load_time=dataset2.loc[i, 'plate_load_time'], mlb_load_time=dataset2.loc[i, 'mlb_load_time'], qpcr_mix_lot=dataset2.loc[i, 'qpcr_mix_lot'], mgisp_tips_lot=dataset2.loc[i, 'mgisp_tips_lot'], machine_operator=dataset2.loc[i, 'machine_operator'])
						db.session.add(run_summary)
						db.session.commit()
					except Exception as error:
						db.session.rollback()
					
			except KeyError:
				pass
				
		print(dataset2[['mlb_load_time']].head(50))
	return render_template('data_upload.html', form=form, form2=form2)
	

@app.route('/retests', methods=['GET', 'POST'])
def retests():
	'''file_loc = #C:/MAMP/htdocs/schedule-maker/app/static/retest_april.csv'
	names = ['sample_id', 'plate_id', 'well', 'fam', 'vic', 'analyst', 'retest_type', 'reason']
	dataset = concat((chunk for chunk in read_csv(file_loc, names=names, chunksize=5000, keep_default_na=False)))#read_csv(file_loc, chunksize=1000, sep='\n')
	
	#print(dataset.loc[52, 'well'])
	for i in range(1, len(dataset)):
		retest_query = Retests.query.filter_by(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well']).first()
		if not retest_query:
			if dataset.loc[i, 'sample_id'] is not '' or '\\':
				if dataset.loc[i, 'sample_id'] and dataset.loc[i, 'plate_id'] and dataset.loc[i, 'well'] is not '':
					if dataset.loc[i, 'fam'] and dataset.loc[i, 'vic'] is not '':
						retests_data = Retests(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well'], fam=dataset.loc[i, 'fam'], vic=dataset.loc[i, 'vic'], analyst=dataset.loc[i, 'analyst'], retest_type=dataset.loc[i, 'retest_type'])
						db.session.add(retests_data)
						db.session.commit()
					elif dataset.loc[i, 'fam'] is '' and dataset.loc[i, 'vic'] is not '':
						retests_data = Retests(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well'], vic=dataset.loc[i, 'vic'], analyst=dataset.loc[i, 'analyst'], retest_type=dataset.loc[i, 'retest_type'])
						db.session.add(retests_data)
						db.session.commit()
					elif dataset.loc[i, 'vic'] is '' and dataset.loc[i, 'fam'] is not '':
						retests_data = Retests(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well'], fam=dataset.loc[i, 'fam'], analyst=dataset.loc[i, 'analyst'], retest_type=dataset.loc[i, 'retest_type'])
						db.session.add(retests_data)
						db.session.commit()
					elif dataset.loc[i, 'fam'] and dataset.loc[i, 'vic'] is '':
						retests_data = Retests(sample_id=dataset.loc[i, 'sample_id'], plate_id=dataset.loc[i, 'plate_id'], well=dataset.loc[i, 'well'], analyst=dataset.loc[i, 'analyst'], retest_type=dataset.loc[i, 'retest_type'])
						db.session.add(retests_data)
						db.session.commit()'''
	#print(type(sample_id), sample_id, type(plate_id), plate_id, type(well), well, type(fam), fam, type(vic), vic, type(analyst), analyst, type(retest_type), retest_type)
	retest_datas = Retests.query.all()
	
	#sample_ids = [rd.sample_id for rd in retest_datas]
	plate_ids = [rd.plate_id for rd in retest_datas]
	plate_date = set([pi.split('-', 1)[0] for pi in plate_ids])
	plate_date_list_ = []
	for item in plate_date:
		plate_date_list_.append(item)
	plate_date_list = sorted(plate_date_list_)
	pd_count_list = []
	for pd in plate_date_list:
		plate_date_search = pd + '%'
		pd_count = Retests.query.filter(Retests.plate_id.like(plate_date_search)).count()
		pd_count_list.append({ str(pd): pd_count})
	#print(pd_count_list)
		
	retests_well_group = Retests.query.group_by(Retests.well).all()#Retests.query.distinct(Retests.well).all()
	for well_group in retests_well_group:
		well_group.well_count = Retests.query.filter_by(well=well_group.well).count()
		#print(well_group.well, well_group.well_count)
		
	max_wellcount = max([well_group.well_count for well_group in retests_well_group])
	
	
	fpd_form = FilterPlateDateForm()
	fpd_form.plate_date.choices = [''] + plate_date_list
	if fpd_form.validate_on_submit():
		return redirect(url_for('retests_plate_date', plate_date=fpd_form.plate_date.data))	
	
	return render_template('retests.html', retests_well_group=retests_well_group, max_wellcount=max_wellcount, plate_date_list=plate_date_list, fpd_form=fpd_form, pd_count_list=pd_count_list)


@app.route('/staff_summary', methods=['GET', 'POST'])
def staff_summary():	
	retest_plate_group = Retests.query.group_by(Retests.plate_id).all()
	
	#dispensing 
	retest_dispense_group = RunSummary1.query.group_by(RunSummary1.sample_dispensing).all()
	for rdg in retest_dispense_group:
		rdg.dispense_count = RunSummary1.query.filter_by(sample_dispensing=rdg.sample_dispensing).count()
		rdg.plates = RunSummary1.query.filter_by(sample_dispensing=rdg.sample_dispensing).all()
		
		rdg.retest_count = 0
		for rc in rdg.plates:
			for rd in retest_plate_group:
				if rc.plate_id == rd.plate_id:
					rdg.retest_count += 1
		
		
	#machine operator
	retest_operator_group = RunSummary1.query.group_by(RunSummary1.machine_operator).all()
	for rog in retest_operator_group:
		rog.processed_count = RunSummary1.query.filter_by(machine_operator=rog.machine_operator).count()
		rog.plates = RunSummary1.query.filter_by(machine_operator=rog.machine_operator).all()
		
		rog.retest_count = 0
		for rc in rog.plates:
			for rd in retest_plate_group:
				if rc.plate_id == rd.plate_id:
					rog.retest_count += 1	
	
	
	
	return render_template('summary.html', retest_dispense_group=retest_dispense_group, retest_operator_group=retest_operator_group)


@app.route('/run_summary', methods=['GET', 'POST'])
def run_summary():	
	retest_plate_group = Retests.query.group_by(Retests.plate_id).all()
	#summary_plate_group = RunSummary1.query.group_by(RunSummary1.plate_id).all()
	
	#run summary
	for rtp in retest_plate_group:
		rtp.summary = RunSummary1.query.filter_by(plate_id=rtp.plate_id).all()
		for rs in rtp.summary:
			rs.dispense_time = datetime.combine(date.today(), rs.dispensing_finish) - datetime.combine(date.today(), rs.dispensing_start)
			#print(type(rs.dispense_time))
			#if rs.dispense_time < timedelta(0, 0, 0):
				#rs.dispense_time = datetime.combine(date.today() + timedelta(days=1), rs.dispensing_finish) - datetime.combine(date.today(), rs.dispensing_start)
			rs.dispense_to_load_time = datetime.combine(date.today(), rs.plate_load_time) - datetime.combine(date.today(), rs.dispensing_finish)
			#if rs.dispense_to_load_time < timedelta(hours=1):
			#rs.dispense_to_load_time = datetime.combine(date.today() + timedelta(hours=1), rs.plate_load_time) - datetime.combine(date.today() + timedelta(hours=1), rs.dispensing_finish)
				
	return render_template('run_summary.html', retest_plate_group=retest_plate_group)
	

@app.route('/retests/<plate_date>', methods=['GET', 'POST'])
def retests_plate_date(plate_date):
	plate_date_search = '%' + plate_date
	retests_well_group = Retests.query.filter(Retests.plate_id.like(plate_date_search)).first()
	for well_group in retests_well_group:
		well_group.well_count = Retests.query.filter_by(well=well_group.well).count()
		#print(well_group.well, well_group.well_count)
	
	max_wellcount = max([well_group.well_count for well_group in retests_well_group])
	
	plate_date_list = sorted(plate_date_list_)
	fpd_form = FilterPlateDateForm()
	fpd_form.plate_date.choices = [''] + plate_date_list
	return render_template('retests.html', retests_well_group=retests_well_group, max_wellcount=max_wellcount, plate_date_list=plate_date_list, fpd_form=fpd_form)
	