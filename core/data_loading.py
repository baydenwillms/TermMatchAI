'''
You can use this repository: https://github.com/NOAA-Omics/noaa-omics-templates to get your lists of terms,
Or, Copy and Paste
'''

def get_term_lists():
	
	# Water_sample_data from Version 2 data template
	noaa_template_terms=['sample_name', 'sample_type', 'serial_number', 'cruise_id', 'line_id', 'station', 'locationID', 'habitat_natural_artificial_0_1', 
						'ctd_bottle_no', 'sample_replicate', 'source_material_id', 'biological_replicates', 'extract_number', 'sample_title', 'bioproject_accession', 
						'biosample_accession', 'notes_sampling', 'amplicon_sequenced', 'metagenome_sequenced', 'organism', 'verbatimEventDate', 'eventDate', 'minimumDepthInMeters', 
						'maximumDepthInMeters', 'env_broad_scale', 'env_local_scale', 'env_medium', 'geo_loc_name', 'waterBody', 'country', 'decimalLatitude', 'decimalLongitude', 'collection_method', 
						'samp_collect_device', 'samp_size', 'samp_size_unit', 'samp_vol_we_dna_ext', 'samp_vol_ext_unit', 'samp_mat_process',
						'filter_passive_active_0_1', 'filter_onsite_dur', 'size_frac', 'sterilise_method', 'samp_store_dur', 'samp_store_loc', 'samp_store_temp', 
						'samp_store_sol', 'description', 'date_modified', 'modified_by']

	# New (incoming) data template
	user_terms=['eventID', 'country', 'decimalLatitude', 'decimalLongitude', 'eventEnteredBy', 'locality', 'yearCollected', 'samplingProtocol', 'collectorList', 
				'continentOcean', 'county', 'dayCollected', 'depthOfBottomInMeters', 'habitat', 'horizontalDatum', 'island', 'islandGroup', 'landowner', 'maximumDepthInMeters', 
				'maximumElevationInMeters', 'coordinateUncertaintyInMeters', 'microHabitat', 'minimumDepthInMeters', 'minimumElevationInMeters', 'monthCollected', 'permitInformation', 
				'eventRemarks', 'stateProvince', 'taxTeam', 'timeOfDay', 'verbatimLatitude', 'verbatimLongitude', 'environmentalMedium', 'permitType', 'permitText', 'permitURI', 'permitStatus', 
				'recordedByID', 'bcid', 'expeditionCode', 'projectId']
	
	return(noaa_template_terms, user_terms)


def get_terms_with_data():

	# Water_sample_data from Version 2 data template (WITH A SAMPLE PIECE OF DATA)
	noaa_terms_w_data={'sample_name': 'GOMECC4_27N_Sta1_DCM_A', 'sample_type': 'seawater', 'serial_number': 'GOMECC4_004', 'cruise_id': 'GOMECC-4 (2021)', 
'line_id': '27N', 'station': 'Sta1', 'locationID': '27N_Sta1', 'habitat_natural_artificial_0_1': None, 'ctd_bottle_no': '14', 'sample_replicate': 'A', 'source_material_id': 'GOMECC4_27N_Sta1_DCM', 'biological_replicates': 'GOMECC4_27N_Sta1_DCM_B, GOMECC4_27N_Sta1_DCM_C', 'extract_number': 'Plate4_53', 'sample_title': 'Atlantic Ocean seawater sample GOMECC4_27N_Sta1_DCM_A', 'bioproject_accession': 'PRJNA887898', 'biosample_accession': 'SAMN37516094', 'notes_sampling': 'Only enough water for 2 surface replicates. ', 'amplicon_sequenced': 'SSU 16S V4-V5 | 18S V9', 'metagenome_sequenced': 'planned for FY24', 'organism': 'seawater metagenome', 'verbatimEventDate': '2021-09-14T11:00-04:00', 'eventDate': '2021-09-14T07:00', 'minimumDepthInMeters': '49', 'maximumDepthInMeters': '49', 'env_broad_scale': 'marine biome [ENVO:00000447]', 'env_local_scale': 'marine photic zone [ENVO:00000209]', 'env_medium': 'sea water [ENVO:00002149]', 'geo_loc_name': 'USA: Atlantic Ocean, east of Florida (27 N)', 'waterBody': 'Mexico, Gulf of', 'country': 'US', 'decimalLatitude': '26.997', 'decimalLongitude': '-79.618', 'collection_method': 'CTD rosette', 'samp_collect_device': 'Niskin bottle', 'samp_size': None, 'samp_size_unit': None, 'samp_vol_we_dna_ext': '1540', 'samp_vol_ext_unit': 'ml', 'samp_mat_process': 'Pumped through Sterivex filter (0.22-µm) using peristaltic pµmp', 'filter_passive_active_0_1': None, 'filter_onsite_dur': None, 'size_frac': '0.22 µm', 'sterilise_method': None, 'samp_store_dur': None, 'samp_store_loc': None, 'samp_store_temp': None, 'samp_store_sol': None, 'description': 'description of the sample or event', '6/24/2024': '6/24/2024', 'aomlomics@gmail.com': 'aomlomics@gmail.com'}
	
	# New (incoming) data template (WITH A SAMPLE PIECE OF DATA)
	GEOME_terms_w_data={'eventID': 'EX2107_D01_01', 'country': 'USA', 'decimalLatitude': 31.21016, 'decimalLongitude': -77.85317, 'eventEnteredBy': 'Allen Collins', 'locality': 'Blake Plateau: Reef Tracts', 'yearCollected': 2021, 'samplingProtocol': '1.7 liters water by Niskin on D2', 'collectorList': 'NOAA Ocean Exploration', 'continentOcean': 'Atlantic Ocean', 'county': None, 'dayCollected': 27, 'depthOfBottomInMeters': 870, 'habitat': 'oceanic mesopelagic zone biome', 'horizontalDatum': None, 'island': 'Puerto Rico', 'islandGroup': 'Greater Antilles', 'landowner': None, 'maximumDepthInMeters': 505.09, 'maximumElevationInMeters': None, 'coordinateUncertaintyInMeters': None, 'microHabitat': 'Deep Scattering Layer', 'minimumDepthInMeters': 505.09, 'minimumElevationInMeters': None, 'monthCollected': 10, 'permitInformation': None, 'eventRemarks': 'Midwater', 'stateProvince': None, 'taxTeam': None, 'timeOfDay': '20211027T131133', 'verbatimLatitude': None, 'verbatimLongitude': None, 'environmentalMedium': 'sea water', 'permitType': None, 'permitText': None, 'permitURI': None, 'permitStatus': None, 'recordedByID': None, 'bcid': 'https://n2t.net/ark:/21547/Fff2EX2107_D01_01', 'expeditionCode': 'EX2107_eDNA', 'projectId': 575}

	return(noaa_terms_w_data, GEOME_terms_w_data)